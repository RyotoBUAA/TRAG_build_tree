# -*- encoding:utf-8 -*-

import os
from openai import OpenAI

# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:8001'
# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:8001'

os.environ["OPENAI_API_KEY"] = "想要api？没门！"
os.environ["OPENAI_BASE_URL"] = "https://xiaoai.plus/v1"

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_BASE_URL")
)


def process_result(result):
    for mark in ["\"", "\'"]:
        result = result.replace(mark, "")
    return result


def relation_extract_str(content):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content":
                        '''
        我会给你几个文本，请你识别其中包含的从属关系，这些关系以二元对的形式出现，即以元组(a, b)表示b是a的父节点，
        这些关系最终可以形成若干棵树。需要注意的是，二元对不可以出现可以传递的关系，例如(a, b)和(b, c)存在时，
        (a, c)不可以存在，因为前两个元组已经表示了这样的间接从属关系。
        
        请注意：你的输出只可以包含若干 (a, b) 这样形式的二元对，即有英文左括号、子节点、逗号、父节点、英文右括号，
        不可以包含任何其他信息，包括“根据提供的文本”这样的话语。每个二元对以换行符分隔；a和b不可以过长，
        只可以包含关键词；从属关系必须划分较细，不可以一个节点包含过多信息。后一个节点b一定是节点a的父节点，不可以颠倒顺序。
        而且不可以有回路（比如(u,v)、(v,w)、(w,u)同时存在是不允许的）！
                        ''',
                },
                {
                    "role": "user",
                    "content": content,
                },
            ],
            model="gpt-4",
        )

        result = chat_completion.choices[0].message.content
        relations = []
        d = list(result.split(')'))
        for part in d:
            if "," in part and "(" in part:
                try:
                    u, v = ((part.strip())[1:]).split(",")
                    u = process_result(u)
                    v = process_result(v)
                    relations.append([u, v])
                except Exception as e:
                    pass
        return relations
    except Exception as e:
        print(f"GPT Error: {e}")
        return []
