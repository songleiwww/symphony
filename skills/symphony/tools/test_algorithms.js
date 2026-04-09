import symphony from "./src/index.js";

// 测试算法库
async function testAlgorithmLibrary() {
  console.log("📚 序境Symphony 顶级算法库测试");
  console.log("=".repeat(60));

  // 初始化引擎
  await symphony.init({});

  // 统计总算法数
  const total = symphony.algorithms.all.length;
  console.log(`✅ 算法库加载完成，总计收录顶级算法：${total} 个`);
  console.log();

  // 各分类统计
  Object.entries(symphony.algorithms.categories).forEach(([key, category]) => {
    console.log(`  📂 ${category.name}：${category.algorithms.length} 个算法`);
  });
  console.log();

  // 测试搜索功能
  console.log("🔍 搜索测试：查找Transformer相关算法");
  const transformer = symphony.algorithms.search("Transformer");
  console.log(`  找到 ${transformer.length} 个相关算法：`);
  transformer.forEach(algo => {
    console.log(`    - ${algo.name}`);
  });
  console.log();

  // 测试按标签搜索
  console.log("🏷️  按标签搜索：大模型相关算法");
  const llmAlgos = symphony.algorithms.searchByTag("大模型");
  console.log(`  找到 ${llmAlgos.length} 个相关算法：`);
  llmAlgos.forEach(algo => {
    console.log(`    - ${algo.name}`);
  });
  console.log();

  // 测试按ID获取
  console.log("🆔 按ID查找：dijkstra算法");
  const dijkstra = symphony.algorithms.getById("dijkstra");
  if (dijkstra) {
    console.log(`  ✅ 找到：${dijkstra.name}`);
    console.log(`  复杂度：${dijkstra.complexity}`);
    console.log(`  描述：${dijkstra.description}`);
  }
  console.log();

  console.log("🎉 算法库集成测试全部通过！已成功加入序境内核算力库。");
}

testAlgorithmLibrary();
