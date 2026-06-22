# abab$ phase trace

이 페이지는 Ukkonen 알고리즘을 `abab$`로 아주 작게 추적합니다. 실제 구현마다 active point 표현은 조금씩 다르지만, phase마다 "기존 edge를 따라갈 수 있는가", "어디서 split이 생기는가", "suffix link로 다음 suffix를 어떻게 처리하는가"는 같습니다.

## 표기

아래 표에서는 active point를 `(node, edge, length)`로 적습니다.

| 표기 | 의미 |
| --- | --- |
| `root` | suffix tree root |
| `edge=a` | root 또는 현재 node에서 `a`로 시작하는 edge 위에 있음 |
| `length=2` | active edge를 2글자 내려간 위치 |
| Rule 3 | 다음 문자가 이미 있어서 이번 phase가 implicit하게 끝남 |

Sentinel `$`는 입력 alphabet에 없는 문자라고 가정합니다.

## Phase 0: `a`

처음에는 root에 아무 edge도 없습니다. 새 문자 `a`를 넣으면 suffix `a`를 나타내는 leaf를 만듭니다.

```text
root
└── a...
```

| 항목 | 값 |
| --- | --- |
| active point | `(root, -, 0)` |
| 처리 suffix | `a` |
| 동작 | root에 `a` edge leaf 생성 |
| phase 후 active | `(root, -, 0)` |

## Phase 1: `ab`

새 문자 `b`를 붙입니다. root에 `b` edge가 없으므로 suffix `b` leaf를 만듭니다.

```text
root
├── ab...
└── b...
```

| 항목 | 값 |
| --- | --- |
| active point | `(root, -, 0)` |
| 처리 suffix | `b` |
| 동작 | root에 `b` edge leaf 생성 |
| phase 후 active | `(root, -, 0)` |

## Phase 2: `aba`

새 문자 `a`를 붙입니다. root에는 이미 `a`로 시작하는 edge가 있고, 다음 문자가 일치합니다. 그래서 새 leaf를 만들지 않고 implicit tree 상태로 멈춥니다.

```text
root
├── aba...
└── ba...
```

| 항목 | 값 |
| --- | --- |
| active point | `(root, edge=a, length=0)` |
| 본 문자 | `a` |
| 동작 | 기존 `a` edge를 따라감, Rule 3 |
| phase 후 active | `(root, edge=a, length=1)` |

이 시점의 suffix `a`는 root의 `a...` edge 중간에서 끝납니다. sentinel이 없으면 이런 implicit suffix가 끝까지 남을 수 있습니다.

## Phase 3: `abab`

새 문자 `b`를 붙입니다. active edge `a...`에서 한 글자 내려간 위치 다음 문자가 `b`이고, 새 문자와 일치합니다. 다시 Rule 3으로 멈춥니다.

| 항목 | 값 |
| --- | --- |
| active point | `(root, edge=a, length=1)` |
| 본 문자 | `b` |
| 동작 | 기존 edge 위에서 `ab`까지 진행, Rule 3 |
| phase 후 active | `(root, edge=a, length=2)` |

아직 `ab`와 `b` suffix는 명시 leaf로 분리되지 않았습니다. 반복 문자열에서 Ukkonen이 빠른 이유가 여기에 있습니다. 매 suffix를 강제로 leaf로 만들지 않고, 이미 있는 경로와 맞으면 phase를 멈춥니다.

## Phase 4: `abab$`

Sentinel `$`를 붙이면 더 이상 기존 edge와 맞지 않으므로 밀린 implicit suffix들이 한꺼번에 명시됩니다.

먼저 active point는 root의 `a...` edge를 `ab`만큼 내려간 위치입니다. 다음 글자는 원래 `a`인데 새 문자는 `$`라서 mismatch입니다.

```text
root
└── ab
    ├── ab$
    └── $
```

| 처리 suffix | active 위치 | 동작 |
| --- | --- | --- |
| `ab$` | `a...` edge의 `ab` 뒤 | edge를 `ab`에서 split하고 `$` leaf 생성 |
| `b$` | suffix link/root 규칙으로 `b...` edge 위 | `b` 뒤에서 split하고 `$` leaf 생성 |
| `$` | root | root에 `$` leaf 생성 |

완성된 구조를 개념적으로 그리면 아래와 같습니다.

```text
root
├── ab
│   ├── ab$
│   └── $
├── b
│   ├── ab$
│   └── $
└── $
```

여기서 root 아래 `ab` node와 `b` node가 internal node입니다. 첫 split으로 생긴 internal node의 suffix link는 다음 suffix인 `b` node로 이어지고, 마지막에는 root로 돌아갑니다.

## 코드와 연결하기

위 trace를 구현 함수에 대응시키면 아래처럼 읽을 수 있습니다.

| trace 사건 | 코드에서 보는 함수 |
| --- | --- |
| 기존 edge를 따라가며 Rule 3으로 멈춤 | `go(active, position, position + 1)` 성공 |
| edge 중간 mismatch | `split(active)`로 internal node 생성 |
| 새 suffix leaf 생성 | `tree.push_back(Node(position, s.size(), middle))` |
| 다음 suffix 처리 위치로 이동 | `active.v = getLink(middle)` |
| root에서 첫 글자 skip | `skipRootCharacter` 처리 |

디버깅할 때는 phase마다 active point와 생성된 internal node의 edge label을 출력하는 것이 좋습니다. `abab$`, `banana$`, `aaaa$`처럼 반복이 있는 문자열에서 split 위치와 suffix link가 맞으면 큰 입력에서도 안정적입니다.
