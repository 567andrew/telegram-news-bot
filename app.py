import time

print("🔥 第1步：程序启动")

try:
    import os
    print("✅ 第2步：import os OK")
except Exception as e:
    print("❌ os错误:", e)

try:
    import requests
    print("✅ 第3步：requests OK")
except Exception as e:
    print("❌ requests错误:", e)

try:
    import feedparser
    print("✅ 第4步：feedparser OK")
except Exception as e:
    print("❌ feedparser错误:", e)

try:
    from openai import OpenAI
    print("✅ 第5步：openai OK")
except Exception as e:
    print("❌ openai错误:", e)

print("🚀 开始循环")

while True:
    try:
        print("🔄 程序活着")
    except Exception as e:
        print("❌ 循环错误:", e)

    time.sleep(5)
