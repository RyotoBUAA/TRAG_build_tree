import os
import qianfan


os.environ["QIANFAN_ACCESS_KEY"] = "ALTAKGCdJoFc7vsB6phEjLXfcg"
os.environ["QIANFAN_SECRET_KEY"] = "35ba9a45e7f24cc780da296aa03ea4d3"

chat_comp = qianfan.ChatCompletion()


def model_chat(prompt):

    pre = '''
    
我会给你几段文本，请你识别其中包含的从属关系，这些关系以二元对的形式出现，即以元组(a, b)表示b是a的父节点，
这些关系最终可以形成若干棵树。需要注意的是，二元对不可以出现可以传递的关系，例如(a, b)和(b, c)存在时，
(a, c)不可以存在，因为前两个元组已经表示了这样的间接从属关系。

请注意：你的输出只可以包含若干 a, b 这样形式的二元对，即有子节点、逗号、父节点，
不可以包含任何其他信息，包括“根据提供的文本”这样的话语。每个二元对以换行符分隔；a和b不可以过长，
只可以包含关键词；从属关系必须划分较细，不可以一个节点包含过多信息。b一定是a的父节点，不可以颠倒顺序。
而且不可以有回路！

下面给出文本：
    
    '''

    print(pre+prompt)

    resp = chat_comp.do(model="ERNIE-3.5-128K", messages=[{
        "role": "user",
        "content": pre+prompt
    }])

    return resp["body"]["result"]
