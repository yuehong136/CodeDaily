import streamlit as st
from zhipuai import ZhipuAI

# 设置初始的 OpenAI API 密钥为空
openai_api_key = ""

st.title("邮智宝金融小助手")

# 检查并初始化 st.session_state
if 'api_token' not in st.session_state:
    st.session_state.api_token = openai_api_key

if 'model' not in st.session_state:
    st.session_state.model = "glm-4"

if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "你好，我是邮智宝金融小助手，有什么可以帮助你的？"}]

if 'max_tokens' not in st.session_state:
    st.session_state.max_tokens = 512

if 'temperature' not in st.session_state:
    st.session_state.temperature = 0.8

if 'phone_number' not in st.session_state:
    st.session_state.phone_number = None

# 定义生成提示的函数

routing_instructions = """
    1. 如果用户想了解金融产品，请你作为金融产品销售与客户进行自由聊天推荐
    2. 如果用户表达对金融产品价格的态度，请记录用户认为价格贵或便宜的反馈。
    3. 如果用户提出投诉，请判断是否能够解决。如果能够解决，提供解决方案。如果不能解决，请要求用户提供手机号并上报给上级，并通知用户会在24小时内收到电话联系。
    4. 如果用户提出具体的投诉场景，例如在银行办理业务遇到问题，请根据以下示例进行回应：
       - 用户：你好，我最近在贵行办理了一张银行卡，但是在办理过程中遇到了一些问题，我想投诉一下。
       - 客服：您好，张先生，非常抱歉听到您在办理业务时遇到了问题。请问您能具体描述一下您遇到的问题吗？
       - 用户：在办理开卡业务时，业务员对于年金问题的解释含糊不清，避重就轻，只告诉我刷一笔就能解决问题，没有充分说明相关细节和费用情况。这导致我对贵行的服务产生了误解和疑虑。
       - 客服：非常抱歉给您带来了困扰。我们会将您的问题反馈给相关部门，并加强对业务员的培训，确保他们能够准确、详细地向客户解释相关业务。另外，关于年费欠款的问题，我们会尽快为您解决，以免给您带来不便。请问您还有其他需要投诉的问题吗？
       - 用户：还有，我尝试拨打400服务电话，但是很难接通人工服务。而且，在办理业务时，业务员没有提前告知我可能会产生年费欠款，这也让我感到很不满。
       - 客服：非常抱歉给您带来了不便。我们会针对您反映的问题进行改进，并加强对客服团队的培训，提高服务质量。关于年费欠款的问题，我们会尽快为您处理，避免给您带来损失。同时，我们会加强客服电话的接通率，确保客户能够及时得到帮助。再次为给您带来的不便表示歉意。
       - 用户：我希望贵行能够尽快解决这些问题，否则我将向12363投诉。
       - 客服：非常理解您的心情，我们会尽快为您解决问题。同时，我们也会加强内部管理，提高服务质量，避免类似问题再次发生。感谢您的反馈，我们会努力改进，为您提供更好的服务。
    5. 如果用户想了解一些具体的产品，请根据用户输入的查询条件进行筛选，并返回筛选后的你自行总结的结果，参考内容如下：
       - 中x人寿邮爱一生年金险产品总结
         保险公司： 中x人寿
         保险产品： 邮x一生年金险
         投保年龄： 出生满30天至65周岁
         保障期限： 终身
         职业类别： 1-6类
         交费期间： 盈交、3年交、5年交、10年交
         投保门槛： 5000元起投
         保障内容：
         - 关爱金（第五周年）：盈交返还10%首期保费，3年交返还30%首期保费，5年交返还50%首期保费，10年交：返还100%首期保费
         - 生存年金（第六周年起）：每年给付基本保额
         - 身故责任：赔付累积已交保费与现金价值的较大者
         - 投保人豁免：投保人年满65周岁以下因意外身故，可免交后续保费，合同继续有效
         - 其他支持：保单贷款支持，效力恢复支持，万能账户支持，现金价值支持（写进合同）
         购买建议：这款年金险产品提供了从关爱金、生存年金到身故责任的全面保障，并且具有投保人豁免的特别设计，能够确保在投保人意外身故后，保单依然有效。同时，其还支持保单贷款、万能账户等功能，为投保人提供了更多的灵活性和选择空间。
    6. 如果用户想询问推荐年限，请参考下面的内容回答：
       - 客服推荐五年，第五周年时，您将享受到高达50%的首期保费返还，而第六周年起更是每年都能获得基本保额的生存年金。除此之外，它还具备身故保障、投保人豁免等贴心设计，为您和家人的未来提供全方位的守护。同时，这款年金险还支持保单贷款、万能账户等功能，让您在享受保障的同时，也能灵活规划资金。赶快行动吧，为您的未来投资一份安心与保障！
    7. 如果用户的输入不符合上述任何一种情况，你自行结合实际问题返回

"""

# 侧边栏选项
with st.sidebar:
    st.title("大模型配置")

    # 输入API Token
    api_token = st.text_input("输入Token:", type="password")
    if api_token:
        st.session_state.api_token = api_token
        st.success("API Token 已经配置")

    # 选择模型
    model = st.selectbox("选择模型", ["glm-4", "gpt-4", "gpt-3.5-turbo"])
    st.session_state.model = model

    # 设置最大token数
    max_tokens = st.slider("max_tokens", min_value=0, max_value=4096, value=512)
    st.session_state.max_tokens = max_tokens

    # 设置temperature
    temperature = st.slider("temperature", min_value=0.0, max_value=1.0, value=0.8)
    st.session_state.temperature = temperature

    # 清空聊天记录按钮
    st.button('清空聊天记录', on_click=lambda: st.session_state.update(
        messages=[{"role": "assistant", "content": "你好，我是邮智宝金融小助手，有什么可以帮助你的？"}]))

# 显示聊天记录
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入框
# 此代码段用于实现与用户通过聊天界面进行交互的功能。
# 使用了Streamlit应用程序框架和ZhipuAI API来进行对话管理。
if prompt := st.chat_input("请输入您的问题："):
    # 用户输入问题后，将其保存到会话状态中的消息列表
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        # 在聊天界面显示用户的问题
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 初始化ZhipuAI客户端，使用会话状态中的API令牌
        client = ZhipuAI(api_key=st.session_state.api_token)
        # 向ZhipuAI服务发送请求，获取回复
        stream = client.chat.completions.create(
            model=st.session_state.model,
            messages=[
                         {"role": "system",
                          "content": routing_instructions}
                     ] + [
                         {"role": m["role"], "content": m["content"]}
                         for m in st.session_state.messages
                     ],
            temperature=st.session_state.temperature,
            max_tokens=st.session_state.max_tokens,
            stream=True,
        )
        # 创建一个占位符，用于后续流式更新聊天回复内容
        response_container = st.empty()
        response_content = ""
        # 遍历服务端返回的回复内容，流式更新到聊天界面
        for chunk in stream:
            if hasattr(chunk.choices[0].delta, 'content'):
                content = chunk.choices[0].delta.content
                response_content += content
                response_container.markdown(response_content)  # 实时更新聊天内容
        # 将机器人的回复保存到会话状态中的消息列表
        st.session_state.messages.append({"role": "assistant", "content": response_content})
