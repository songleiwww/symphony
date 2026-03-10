# symphony

#### 浠嬬粛
Symphony锛堜氦鍝嶏級鏄彶涓婃渶寮哄妯″瀷鍗忎綔璋冨害绯荤粺锛佹敮鎸佸妯″瀷骞惰璋冪敤銆佹晠闅滆浆绉汇€佷换鍔¤皟搴︾瓑鍔熻兘銆?
#### 杞欢鏋舵瀯
- 浠诲姟璋冨害锛氭櫤鑳藉垎閰嶄换鍔★紝鎻愬崌鏁堢巼
- 妯″瀷绠＄悊锛氭敮鎸?3+妯″瀷锛堟櫤璋便€佺伀灞便€丯VIDIA銆丮odelScope绛夛級
- 瀹归敊绯荤粺锛氳嚜鍔ㄦ晠闅滆浆绉伙紝纭繚鏈嶅姟姘哥画
- 璁板繂绯荤粺锛氱煭鏈?闀挎湡/宸ヤ綔/鎯呮櫙鍥涚璁板繂
- 鍗忎綔缂栨帓锛氬妯″瀷鍗忓悓宸ヤ綔

#### 瀹夎鏁欑▼

1. 瀹夎鏈€鏂扮増鏈?```bash
pip install symphony-ai
```

2. 瀹夎鎸囧畾鐗堟湰
```bash
pip install symphony-ai==1.0.0
```

3. 浠庢簮鐮佸畨瑁?```bash
git clone https://github.com/songleiwww/symphony.git
cd symphony
pip install -r requirements.txt
cp config.template.py config.py
# 缂栬緫 config.py 濉叆浣犵殑API瀵嗛挜
```

#### 浣跨敤璇存槑

```python
from symphony import SymphonyCore

# 鍒涘缓浜ゅ搷瀹炰緥
symphony = SymphonyCore()

# 鍙戣捣鍗忎綔浠诲姟
result = symphony.dispatch("甯垜瀹夋帓涓€涓?浜哄洟闃熻璁轰細")

# 鑾峰彇绯荤粺鐘舵€?status = symphony.get_status()
print(status)
```

#### 鍙備笌璐＄尞

1. Fork 鏈粨搴?2. 鏂板缓 Feat_xxx 鍒嗘敮
3. 鎻愪氦浠ｇ爜
4. 鏂板缓 Pull Request

#### 鐗规妧

1. 澶氭ā鍨嬪苟琛岋細鍚屾椂璋冪敤澶氫釜AI妯″瀷锛屽崗鍚屽伐浣?2. 鏅鸿兘瀹归敊锛氳嚜鍔ㄦ晠闅滆浆绉伙紝纭繚鏈嶅姟姘哥画
3. 浠诲姟璋冨害锛氭櫤鑳藉垎閰嶄换鍔★紝鎻愬崌鏁堢巼
4. 妯″瀷鐑彃鎷旓細杩愯鏃跺姩鎬佸垏鎹㈡ā鍨?5. 璐熻浇鍧囪　锛氬悎鐞嗗垎閰嶈绠楄祫婧?6. 璺ㄥ钩鍙版敮鎸侊細Windows/Linux/Mac鍏ㄩ潰鍏煎

#### 鑱旂郴鏂瑰紡

- 閭: songlei_www@qq.com
- 闂鍙嶉: GitHub Issues

---

*鏅洪煹浜ゅ搷锛屽叡鍒涘崕绔?

