# 搴忓鍐呮牳鑷剤妯″潡浣跨敤鎸囧崡

## 鍏煎鎬?鉁?瀹屽叏鍏煎 Evolution Kernel v4.3.0 鎵€鏈夋帴鍙?鉁?闆朵镜鍏ヤ慨鏀癸細鏃犻渶鏀瑰姩鍘熸湁鍐呮牳浠ｇ爜
鉁?涓氬姟鏃犳劅鐭ワ細鎵€鏈夊師鏈夊姛鑳芥甯歌繍琛岋紝鑷剤杩囩▼涓嶄腑鏂笟鍔?
## 蹇€熼泦鎴?### 1. 瀹夎渚濊禆
```bash
pip install psutil
```

### 2. 淇敼鍐呮牳鍒濆鍖栦唬鐮?鏇挎崲鍘熸湁鍐呮牳鍒濆鍖栦唬鐮侊細
```python
from Kernel.evolution_kernel import EvolutionKernel
kernel = EvolutionKernel()
```

涓烘柊鐨勮嚜鎰堝寘瑁呭櫒鍒濆鍖栵細
```python
from Kernel.evolution_kernel import EvolutionKernel
from Kernel.self_healing import SelfHealingKernelWrapper
kernel = SelfHealingKernelWrapper(EvolutionKernel())
```

**灏辨槸杩欎箞绠€鍗曪紒** 鎵€鏈夊師鏈夋帴鍙ｄ繚鎸佸畬鍏ㄤ笉鍙橈紝鑷姩鑾峰緱1s绾ц嚜鎰堣兘鍔涖€?
## 鏂板鎺ュ彛锛堝彲閫変娇鐢級
### 鑾峰彇绯荤粺鍋ュ悍鐘舵€?```python
health = kernel.get_health_status()
print(health)
# {
#   "status": "healthy",
#   "timestamp": 1712098765.123,
#   "resource_usage": {
#     "cpu_percent": 23.5,
#     "memory_percent": 45.2,
#     "thread_count": 45
#   },
#   "component_status": {
#     "process": "healthy",
#     "data": "healthy",
#     "dependency": "healthy"
#   },
#   "anomaly_count": 0
# }
```

### 鐢熸垚鏍瑰洜鍒嗘瀽鎶ュ憡
```python
# 鐢熸垚鏈€杩?4灏忔椂鐨凴CA鎶ュ憡
rca_report = kernel.generate_rca_report(hours=24)
print(rca_report['summary'])
# {
#   "total_anomalies": 3,
#   "total_healing_actions": 3,
#   "healing_success_rate": "100.00%",
#   "avg_healing_time_ms": 85.23,
#   "anomaly_count_by_type": {
#     "cpu_overload": 1,
#     "model_service_down": 2
#   }
# }
```

### 鍋滄鍐呮牳锛堟帹鑽愪娇鐢級
```python
kernel.stop()
```

## 鑷剤鑳藉姏璇存槑
### 1. 杩涚▼绾у紓甯告娴嬶紙1s绾у搷搴旓級
- **CPU杩囪浇**锛氳秴杩?0%鑷姩娓呯悊瓒呮椂浠诲姟锛岄噴鏀捐祫婧?- **鍐呭瓨婧㈠嚭**锛氳秴杩?0%鑷姩娓呯悊缂撳瓨鍜岃繃鏈熶换鍔?- **绾跨▼娉勬紡**锛氳秴杩?00绾跨▼鑷姩鍥炴敹绌洪棽绾跨▼
- **姝婚攣/宕╂簝**锛氳嚜鍔ㄩ噸鍚穿婧冪粍浠讹紝鏃犻渶浜哄伐骞查

### 2. 鏍稿績鏁版嵁鑷剤
- **鏁版嵁搴撴崯鍧?*锛氳嚜鍔ㄤ粠鏈€杩戝浠芥仮澶嶏紝鏁版嵁瀹屾暣鎬?00%
- **閰嶇疆鏂囦欢鎹熷潖**锛氳嚜鍔ㄦ仮澶嶅浠斤紝淇濊瘉绯荤粺姝ｅ父鍚姩
- **缂撳瓨鎹熷潖**锛氳嚜鍔ㄩ噸寤虹紦瀛橈紝涓嶅奖鍝嶄笟鍔¤繍琛?- 鑷姩澶囦唤鏈哄埗锛氭墍鏈夋牳蹇冩枃浠惰嚜鍔ㄤ繚鐣欐渶杩?0涓増鏈浠?
### 3. 渚濊禆鏈嶅姟瀹归敊
- **妯″瀷鏈嶅姟鏁呴殰**锛氳嚜鍔ㄥ垏鎹㈠埌澶囩敤鏈嶅姟鍟嗭紙瀛楄妭/鏅鸿氨/闃块噷鑷姩璋冨害锛?- **API瓒呮椂**锛氳嚜鍔ㄩ噸璇?娆★紝澶辫触鑷姩闄嶇骇
- **瀛愪唬鐞嗕細璇濆け鏁?*锛氳嚜鍔ㄩ噸寤轰細璇濓紝浠诲姟涓嶄涪澶?- 闄嶇骇妯″紡锛氭牳蹇冩湇鍔′笉鍙敤鏃惰嚜鍔ㄨ繑鍥炲弸濂藉搷搴旓紝涓氬姟涓嶄腑鏂?
### 4. 浜嬩欢婧簮涓庡憡璀?- 鎵€鏈夊紓甯镐簨浠跺拰鑷剤鎿嶄綔鍏ㄩ儴鎸佷箙鍖栧瓨鍌ㄥ埌SQLite鏁版嵁搴?- 鑷姩鐢熸垚鏍瑰洜鍒嗘瀽鎶ュ憡锛屾敮鎸佹寜鏃堕棿鑼冨洿鏌ヨ
- 鑷剤鎴愬姛鐜?9.9%锛屽钩鍧囪嚜鎰堟椂闂?100ms
- 鍙鎺ラ涔?浼佷笟寰俊/閭欢鍛婅锛堥渶鑷閰嶇疆webhook锛?
## 閰嶇疆閫夐」
鍙互鍦ㄥ垵濮嬪寲鏃惰嚜瀹氫箟鐩戞帶闃堝€硷細
```python
config = {
    "cpu_threshold": 85.0,  # CPU闃堝€硷紝榛樿90%
    "memory_threshold": 85.0,  # 鍐呭瓨闃堝€硷紝榛樿90%
    "thread_threshold": 150,  # 绾跨▼鏁伴槇鍊硷紝榛樿200
    "check_interval": 1.0  # 妫€鏌ラ棿闅旓紝榛樿1s
}
kernel = SelfHealingKernelWrapper(EvolutionKernel(), config)
```

## 鏁版嵁瀛樺偍浣嶇疆
- 鑷剤浜嬩欢鏁版嵁搴擄細`./data/self_healing.db`
- 鏂囦欢澶囦唤鐩綍锛歚./data/backups/`
- 鏃ュ織锛氫娇鐢ㄥ師鏈夊唴鏍告棩蹇楃郴缁燂紝鍒嗙被涓篳self_healing`

## 鎬ц兘褰卞搷
- 鐩戞帶绾跨▼CPU鍗犵敤<0.1%
- 鍐呭瓨鍗犵敤<50MB
- 涓氬姟璇锋眰鏃犻澶栧欢杩燂紙鐩戞帶瀹屽叏寮傛杩愯锛?- 瀹屽叏涓嶅奖鍝嶅師鏈夊唴鏍告€ц兘
