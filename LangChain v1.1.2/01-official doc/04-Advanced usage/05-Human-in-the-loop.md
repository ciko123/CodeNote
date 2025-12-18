# 人在回路 (Human-in-the-loop, HITL)

人在回路 (HITL) [中间件](/oss/python/langchain/middleware/built-in#human-in-the-loop)让您可以为代理工具调用添加人工监督。
当模型提出可能需要审查的操作时——例如写入文件或执行SQL——中间件可以暂停执行并等待决策。

它通过根据可配置的策略检查每个工具调用来实现这一点。如果需要干预，中间件会发出一个[interrupt](https://reference.langchain.com/python/langgraph/types/#langgraph.types.interrupt)来停止执行。图状态使用LangGraph的[持久化层](/oss/python/langgraph/persistence)保存，因此执行可以安全地暂停并在稍后恢复。

然后人工决策决定接下来发生什么：操作可以按原样批准（`approve`）、在运行前修改（`edit`），或带有反馈地拒绝（`reject`）。

## 中断决策类型 (Interrupt decision types)

[中间件](/oss/python/langchain/middleware/built-in#human-in-the-loop)定义了三种内置的人工响应中断的方式：

| 决策类型 | 描述 | 使用示例 |
| ------------- | ------------------------------------------------------------------------- | --------------------------------------------------- |
| ✅ `approve`   | 操作按原样批准并执行，不做任何更改。 | 完全按照书面内容发送邮件草稿 |
| ✏️ `edit`     | 工具调用在修改后执行。 | 在发送邮件前更改收件人 |
| ❌ `reject`    | 工具调用被拒绝，并向对话中添加说明。 | 拒绝邮件草稿并说明如何重写 |

每个工具可用的决策类型取决于您在`interrupt_on`中配置的策略。
当多个工具调用同时暂停时，每个操作需要单独的决策。
决策必须按照操作在中断请求中出现的顺序提供。

  在**编辑**工具参数时，请保守地进行更改。对原始参数的重大修改可能会导致模型重新评估其方法，并可能多次执行工具或采取意外操作。

## 配置中断 (Configuring interrupts)

要使用HITL，在创建代理时将[中间件](/oss/python/langchain/middleware/built-in#human-in-the-loop)添加到代理的`middleware`列表中。

您可以使用工具操作到每个操作允许的决策类型的映射来配置它。当工具调用与映射中的操作匹配时，中间件将中断执行。

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware # [!code highlight]
from langgraph.checkpoint.memory import InMemorySaver # [!code highlight]


agent = create_agent(
    model="gpt-4o",
    tools=[write_file_tool, execute_sql_tool, read_data_tool],
    middleware=[
        HumanInTheLoopMiddleware( # [!code highlight]
            interrupt_on={
                "write_file": True,  # 允许所有决策（approve、edit、reject）
                "execute_sql": {"allowed_decisions": ["approve", "reject"]},  # 不允许编辑
                # 安全操作，无需批准
                "read_data": False,
            },
            # 中断消息的前缀 - 与工具名称和参数组合形成完整消息
            # 例如，"Tool execution pending approval: execute_sql with query='DELETE FROM...'"
            # 单个工具可以通过在中断配置中指定"description"来覆盖此设置
            description_prefix="Tool execution pending approval",
        ),
    ],
    # 人在回路需要检查点来处理中断。
    # 在生产环境中，使用持久化检查点器如AsyncPostgresSaver。
    checkpointer=InMemorySaver(),  # [!code highlight]
)
```

  您必须配置检查点器以在跨中断时持久化图状态。
  在生产环境中，使用持久化检查点器如[`AsyncPostgresSaver`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver)。对于测试或原型开发，使用[`InMemorySaver`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.memory.InMemorySaver)。

  调用代理时，传递包含**线程ID**的`config`，以将执行与对话线程关联。
  详情请参阅[LangGraph中断文档](/oss/python/langgraph/interrupts)。

**配置选项 (Configuration options)**:
  - **interrupt_on** (dict, required):
    工具名称到批准配置的映射。值可以是 `True`（使用默认配置中断）、`False`（自动批准）或 `InterruptOnConfig` 对象。
  
  - **description_prefix** (string, default="Tool execution requires approval"):
    操作请求描述的前缀

  **`InterruptOnConfig` 选项：**

  - **allowed_decisions** (list[string]):
    允许的决策列表：`'approve'`、`'edit'` 或 `'reject'`
  
  - **description** (string | callable):
    用于自定义描述的静态字符串或可调用函数

## 响应中断 (Responding to interrupts)

当您调用代理时，它会运行直到完成或引发中断。当工具调用与您在`interrupt_on`中配置的策略匹配时，会触发中断。在这种情况下，调用结果将包含一个带有需要审查操作的`__interrupt__`字段。然后您可以将这些操作呈现给审查者，并在提供决策后恢复执行。

```python
from langgraph.types import Command

# 人在回路利用LangGraph的持久化层。
# 您必须提供线程ID以将执行与对话线程关联，
# 这样对话就可以暂停和恢复（正如人工审查所需要的）。
config = {"configurable": {"thread_id": "some_id"}} # [!code highlight]
# 运行图直到遇到中断。
result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Delete old records from the database",
            }
        ]
    },
    config=config # [!code highlight]
)

# 中断包含完整的HITL请求，带有action_requests和review_configs
print(result['__interrupt__'])
# > [
# >    Interrupt(
# >       value={
# >          'action_requests': [
# >             {
# >                'name': 'execute_sql',
# >                'arguments': {'query': 'DELETE FROM records WHERE created_at < NOW() - INTERVAL \'30 days\';'},
# >                'description': 'Tool execution pending approval\n\nTool: execute_sql\nArgs: {...}'
# >             }
# >          ],
# >          'review_configs': [
# >             {
# >                'action_name': 'execute_sql',
# >                'allowed_decisions': ['approve', 'reject']
# >             }
# >          ]
# >       }
# >    )
# > ]


# 使用批准决策恢复
agent.invoke(
    Command( # [!code highlight]
        resume={"decisions": [{"type": "approve"}]}  # 或 "edit", "reject" [!code highlight]
    ), # [!code highlight]
    config=config # 相同的线程ID以恢复暂停的对话
)
```

### 决策类型 (Decision types)

  **✅ approve**:
    使用`approve`按原样批准工具调用并执行，不做任何更改。

```python
agent.invoke(
        Command(
            # 决策以列表形式提供，每个审查的操作一个。
            # 决策的顺序必须与`__interrupt__`请求中列出的操作顺序匹配。
            resume={
                "decisions": [
                    {
                        "type": "approve",
                    }
                ]
            }
        ),
        config=config  # 相同的线程ID以恢复暂停的对话
    )
```

  **✏️ edit**:
    使用`edit`在执行前修改工具调用。
    提供带有新工具名称和参数的编辑后操作。

```python
agent.invoke(
        Command(
            # 决策以列表形式提供，每个审查的操作一个。
            # 决策的顺序必须与`__interrupt__`请求中列出的操作顺序匹配。
            resume={
                "decisions": [
                    {
                        "type": "edit",
                        # 带有工具名称和参数的编辑后操作
                        "edited_action": {
                            # 要调用的工具名称。
                            # 通常与原始操作相同。
                            "name": "new_tool_name",
                            # 传递给工具的参数。
                            "args": {"key1": "new_value", "key2": "original_value"},
                        }
                    }
                ]
            }
        ),
        config=config  # 相同的线程ID以恢复暂停的对话
    )
```

          在**编辑**工具参数时，请保守地进行更改。对原始参数的重大修改可能会导致模型重新评估其方法，并可能多次执行工具或采取意外操作。

  **❌ reject**:
    使用`reject`拒绝工具调用并提供反馈而不是执行。

```python
agent.invoke(
        Command(
            # 决策以列表形式提供，每个审查的操作一个。
            # 决策的顺序必须与`__interrupt__`请求中列出的操作顺序匹配。
            resume={
                "decisions": [
                    {
                        "type": "reject",
                        # 关于为什么拒绝操作的说明
                        "message": "No, this is wrong because ..., instead do this ...",
                    }
                ]
            }
        ),
        config=config  # 相同的线程ID以恢复暂停的对话
    )
```

    `message`作为反馈添加到对话中，以帮助代理理解为什么操作被拒绝以及它应该做什么。
    
    ***
    
    ### 多个决策 (Multiple decisions)
    
    当多个操作需要审查时，按照它们在中断中出现的顺序为每个操作提供决策：
    
```python
{
        "decisions": [
            {"type": "approve"},
            {
                "type": "edit",
                "edited_action": {
                    "name": "tool_name",
                    "args": {"param": "new_value"}
                }
            },
            {
                "type": "reject",
                "message": "This action is not allowed"
            }
        ]
    }
```

## 执行生命周期 (Execution lifecycle)

中间件定义了一个`after_model`钩子，它在模型生成响应之后但在任何工具调用执行之前运行：

1. 代理调用模型生成响应。
2. 中间件检查响应中的工具调用。
3. 如果任何调用需要人工输入，中间件构建一个带有`action_requests`和`review_configs`的`HITLRequest`并调用[interrupt](https://reference.langchain.com/python/langgraph/types/#langgraph.types.interrupt)。
4. 代理等待人工决策。
5. 基于`HITLResponse`决策，中间件执行批准或编辑的调用，为拒绝的调用合成[ToolMessage](https://reference.langchain.com/python/langchain/messages/#langchain.messages.ToolMessage)，并恢复执行。

## 自定义HITL逻辑 (Custom HITL logic)

对于更专业化的工作流，您可以直接使用[interrupt](https://reference.langchain.com/python/langgraph/types/#langgraph.types.interrupt)原语和[中间件](/oss/python/langchain/middleware)抽象构建自定义HITL逻辑。

查看上面的[执行生命周期](#execution-lifecycle)以了解如何将中断集成到代理的操作中。

***

  [在GitHub上编辑此页面的源代码。](https://github.com/langchain-ai/docs/edit/main/src/oss/langchain/human-in-the-loop.mdx)

  [通过MCP以编程方式连接这些文档](/use-these-docs)到Claude、VSCode等，以获得实时答案。


---

> 要在此文档中查找导航和其他页面，请在以下位置获取llms.txt文件：https://docs.langchain.com/llms.txt