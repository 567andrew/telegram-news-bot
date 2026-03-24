print("🔥 程序启动成功", flush=True)

while True:
    try:
        print("🔄 正在运行...", flush=True)
        send("✅ Worker 正常运行")
    except Exception as e:
        print("❌ 错误:", e, flush=True)

    time.sleep(60)
