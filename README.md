# PyMudClient: 用 Python 開發的 MUD Client 核心

## 這是什麼？

- MUD, Multi-User Dungeon，是多人即時虛擬類遊戲，通常以文字描述為基礎。
- **pymudclient** 實作了連線、斷線重連、顯示、輸入介面、Alias、Trigger、Timer 的功能。

---

- [PyMudClient: 用 Python 開發的 MUD Client 核心](#pymudclient-用-python-開發的-mud-client-核心)
  - [這是什麼？](#這是什麼)
  - [已測試過環境](#已測試過環境)
  - [支援功能](#支援功能)
  - [安裝](#安裝)
  - [使用範例](#使用範例)
  - [輸入介面](#輸入介面)
  - [API Reference](#api-reference)
    - [run](#run)
    - [Alias](#alias)
      - [Alias class 參數](#alias-class-參數)
      - [使用範例](#使用範例-1)
    - [Trigger](#trigger)
      - [Trigger class 參數](#trigger-class-參數)
      - [使用範例](#使用範例-2)
    - [Timer](#timer)
      - [Timer class 參數](#timer-class-參數)
      - [使用範例](#使用範例-3)
  - [已知問題](#已知問題)
  - [尚未實作功能](#尚未實作功能)
  - [License](#license)

## 已測試過環境

- macOS Ventura 13.3.1 (a)
- GNU/Linux 5.15.0-1032-raspi aarch64

## 支援功能

- 連線：根據輸入的 host 跟 port 進行連線。
- 斷線重連：發生異常、server 重新啟動導致的斷線，會等待 3 秒後重新連線。
- 顯示：顯示 server 回傳的內容。
  - 有處理輸入中文的顯示問題。
  - 只針對萬王之王 (kk.muds.idv.tw:4000) 進行測試過。
- 輸入介面：在最後一行顯示輸入的文字；送出的文字還沒有改動時按下 Enter 會再送一次。

## 安裝

`pip install pymudclient`

## 使用範例

```py
import pymudclient as mud

from aliases import ALIAS_LIST
from settings import (
    HOST,
    PORT,
)
from timers import TIMER_LIST
from triggers import TRIGGER_LIST

mud.run(
    HOST,
    PORT,
    alias_list=ALIAS_LIST,
    trigger_list=TRIGGER_LIST,
    timer_list=TIMER_LIST,
)
```

## 輸入介面

- 輸入的文字會固定出現在最後一行。
- 可使用 左/右/Home/End 移動位置。
- 可使用 Backspace/Ctrl-H 刪除游標位置前面的字元。
- 可使用 Delete 刪除游標位置後面的字元。
- 可使用 Ctrl-W 刪除前面一個 word (仿照 vim 功能)。
- 按下 Enter 送出後，會記住最後一次送出的文字，可以進行編輯，或直接按 Enter 再送一次。

## API Reference

### run

- 連線至 `<host>:<port>`

```py
run(host, port, alias_list=None, trigger_list=None, timer_list=None)
```

- host `string`: 連線的主機網址或 IP。
- port `number`: 連線的主機 port。
- alias_list `list`: (optional) Alias 清單，參考[下面說明](#alias)。
- trigger_list `list`: (optional) Trigger 清單，參考[下面說明](#trigger)。
- timer_list `list`: (optional) Timer 清單，參考[下面說明](#timer)。

### Alias

#### Alias class 參數

- start_text `string`: Alias 的指令，可以包含空格。
- pattern `string`: (optional) 要替換的指令，會傳到 host。
- func `function`: (optional) 要呼叫的 function。
  - function prototype:
    ```py
    def func(text: str) -> str or None:
      ...
    ```
  - `text` 參數會把除了 start_text 外的後面的文字全部傳入。
  - 如果 function 有回傳文字，會傳給 host。

pattern 跟 func 2 選 1。

#### 使用範例

```py
from pymudclient import Alias

ALIAS_LIST = [
    Alias('kk', pattern='kingdom %0'),
    Alias('c', pattern='cast %1 on %2'),
    Alias('draw', pattern='draw %1 %-1'),
]
```

- pattern 中的 %0 為全部參數。以上面的例子，`kk 安安 你好 123`，`%0` 就是 `安安 你好 123`。
- pattern 中的 %1 ~ %n 為第 1 ~ 第 n 個參數。以上面的例子，`c fire stone`，`%1` 就是 `fire`；`%2` 就是 `stone`。
- pattern 中的 %-1 為去掉第 1 個參數後的其他所有參數；%2 為去掉第 2 個參數後的其他所有參數；%n 為去掉第 n 個參數後的其他所有參數。以上面的例子，`draw board ABCD 1234`，`%-1` 就是 `ABCD 1234`。

### Trigger

#### Trigger class 參數

- pattern `string`: 觸發的 pattern，使用 regex。
- data `string`: (optional) 要直接送出的文字，如果是固定文字用這個就好。
- func `function`: (optional) 要呼叫的 function。
  - function prototype:
    ```py
    def func(text: str, match_group: list) -> str or None:
        ...
    ```
  - `text` 參數會把有符合 trigger 條件的整行文字傳入。
  - `match_group` 參數會把 regex match 到的 `match.groups()` 傳入
  - 如果 function 有回傳文字，會傳給 host。

#### 使用範例

```py
from pymudclient import Trigger

def summon(text, match_group):
    return f'summon {match_group[0]}'

TRIGGER_LIST = [
    Trigger(r"^您的英文名字\(新人物請輸入\'new\'\) :$", data=USER),
    Trigger(r"^請輸入密碼﹕$", data=PW),
    Trigger(r'\(([a-zA-Z]+)\)告訴你﹕sum$', func=summon),
]
```

- 前面 2 個是輸入帳號密碼的 trigger。
- 第 3 個是幫忙把人招喚過來的 trigger，有抓取角色 id。

### Timer

#### Timer class 參數

- seconds `number`: 多久執行一次，單位是秒。
- data `string`: (optional) 要直接送出的文字，如果是固定文字用這個就好。
- func `function`: (optional) 要呼叫的 function。
  - function prototype:
    ```py
    def func() -> str or None:
      ...
    ```
  - 如果 function 有回傳文字，會傳給 host。

#### 使用範例

```py
from pymudclient import Timer

TIMER_LIST = [
    Timer(900, data='save'),
]
```

- 每 900 秒傳送一個 `save` 到 host。

## 已知問題

- 目前沒有。

## 尚未實作功能

- 輸入功能的歷史紀錄，可按 上/下 選擇過去送出過的文字。
- 有看過有些 mud 是有小地圖的功能，應該是 host 傳送過來更新的，這功能需要深入研究 mud 的資料傳送規則。

## License

- [MIT](https://github.com/griiid/PyMudClient/blob/master/LICENSE)
