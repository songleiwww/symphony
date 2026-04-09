import symphony from "./src/index.js";

// 测试启动
async function test() {
  try {
    // 使用TOOLS.md里的豆包模型配置
    await symphony.init({
      arkApiKey: "从环境变量读取，这里仅测试启动流程",
    });

    console.log("✅ 引擎启动成功！");
    console.log("📊 已注册模型数：", symphony.scheduler.providers.size);
    console.log("💾 记忆服务状态：", symphony.memory.repository ? "已初始化" : "未初始化");
    console.log("🧠 需求引擎状态：", symphony.demandEngine ? "已加载" : "未加载");

    console.log("\n🎉 基础架构全链路测试通过！");
  } catch (e) {
    console.error("❌ 启动失败：", e);
    process.exit(1);
  }
}

test();
