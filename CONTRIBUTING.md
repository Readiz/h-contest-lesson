# Contributing

h-contest-lesson 저장소는 h-contest 휴리스틱 노트 콘텐츠의 source of truth입니다.

API와 공개 manifest는 이 저장소의 내용을 기준으로 제공됩니다.
따라서 레슨을 수정하거나 추가하려면 이 저장소에 Pull Request를 보내 주세요.

## 기여할 수 있는 내용

현재는 아래 기여를 환영합니다.

1. 오탈자, 맞춤법, 표현 개선
2. 설명이 불명확한 부분 보강
3. C++ 코드 예제 오류 수정
4. 이미지, 링크, 경로 오류 수정
5. 기존 레슨에 예제나 실수 포인트 추가
6. 새 레슨 추가

새 주제 후보와 아직 적절한 h-contest 문제가 없는 연습 문제는 [ROADMAP.md](ROADMAP.md)에 TODO로 관리합니다. 이미 공개된 레슨의 이동 기록과 보강 완료 기록은 [CHANGELOG.md](CHANGELOG.md)에 남깁니다.

## 레슨 수정 방법

기존 레슨은 아래 파일을 수정합니다.

```text
lessons/<lessonId>/lesson.md
```

길이가 긴 레슨은 `lesson.md`를 개요로 두고, 세부 본문을 하위 페이지로 나눌 수 있습니다.

```text
lessons/<lessonId>/pages/<page-id>.md
```

하위 페이지를 추가하거나 삭제하면 `lessons.json`의 해당 레슨에 `pages` 배열을 함께 갱신합니다.

페이지는 독립적인 학습 질문과 전제가 있을 때만 나눕니다. 글자 수나 하위 개념 개수만으로 분할하지 않습니다.

- 같은 알고리즘의 정의, 상태 변화 예시, 구현, 직접적인 활용은 한 본문에서 이어 설명합니다.
- 개요와 하위 본문 하나만 남았다면 하나의 강의로 합치는 것을 기본으로 합니다.
- 예제·연습이 앞의 설명을 바로 확인하는 역할이면 그 설명 옆에 둡니다.
- 서로 다른 문제 모델이나 독립적으로 찾아볼 구현은 별도 페이지로 둘 수 있습니다. 각 페이지는 다른 페이지의 중간 설명을 이어받지 않고 목적과 전제를 밝혀야 합니다.

통합할 때는 단순히 이어 붙이지 않고 중복 도입·선택표·결론을 정리합니다. 고유 예시와 구현 조건은 보존하고, manifest·본문 링크·검증 스크립트의 경로를 함께 갱신합니다.

예:

```text
lessons/dijkstra/lesson.md
lessons/segment-tree/lesson.md
```

## 새 레슨 추가 방법

새 레슨을 추가할 때는 아래 source 파일을 수정해 주세요.

```text
lessons/<new-lesson-id>/lesson.md
lessons.json
```

`lessons.json`에는 새 레슨이 들어갈 `folderId`, `level`, `estimatedMinutes`, `prerequisites`, `nextLessons`, `relatedLessons`를 함께 지정합니다. 하위 페이지가 있으면 `pageId`, `title`, `description`, `order`, `file`을 가진 `pages` 배열을 추가합니다.

현재 공개 분류는 두 가지입니다.

- `heuristic-notes`: 휴리스틱 기본 및 심화 노트. 현재 h-contest 문제 풀이에 바로 쓰는 기본 구현, 모델링, 최적화, 검증 레슨만 들어갑니다.
- `heuristic-reference`: 휴리스틱 참고 노트. 현재 문제 풀이의 직접 범위를 넘는 전통 알고리즘, 이론, 희소 고급 도구, 장기 확장용 레퍼런스 레슨이 들어갑니다. 이 폴더에는 `research-reference`뿐 아니라 직접성이 낮은 `contest-core` 또는 `advanced-contest` 레슨도 들어갈 수 있습니다.

새 폴더를 추가하기보다 위 두 분류 중 하나를 먼저 고릅니다. 주제별 탐색은 `tags`, `difficultyAxes`, `prerequisites`, `nextLessons`, `relatedLessons`, 하위 `pages`로 표현합니다.

문서의 공개 성격이 명확하지 않으면 아래 metadata를 함께 지정합니다.

```json
{
  "status": "draft | review | published",
  "lessonType": "core | implementation | overview | reference | experimental",
  "seriesId": "parametric-optimization",
  "parentLessonId": "parametric-optimization",
  "practiceStatus": "none | todo | linked | verified",
  "implementationStatus": "concept-only | partial | full",
  "audience": "contest-core | advanced-contest | research-reference",
  "difficultyAxes": ["implementation | proof | modeling | selection"]
}
```

`difficultyAxes`는 레슨이 어려운 이유를 표시합니다. 코드와 corner case가 핵심이면 `implementation`, 조건 증명이 핵심이면 `proof`, 수학/그래프 모델로 바꾸는 과정이 핵심이면 `modeling`, 여러 기법 중 무엇을 고를지 판단하는 문서면 `selection`을 사용합니다. 둘 이상이 동시에 필요하면 여러 값을 넣습니다.

`published`인 `core` 또는 `implementation` 레슨은 `practiceStatus: todo` 상태로 둘 수 없습니다. 실제 practice 링크나 저장소 안의 로컬 완결형 연습을 준비한 뒤 정식 구현 레슨으로 올립니다. 실제 문제와 완전 구현이 아직 없으면 `overview` 또는 `reference`로 분류합니다.

이미지가 필요하면 아래 디렉터리에 추가합니다.

```text
lessons/<new-lesson-id>/lesson-assets/
```

그다음 아래 명령으로 파생 파일을 갱신하고 검증합니다.

```bash
python3 scripts/generate_catalog.py
python3 scripts/validate_lessons.py
```

학습 지도에 등록한 강의 ID가 manifest에 없으면 카탈로그 생성과 `--check`가 실패합니다. 강의를 통합하거나 삭제할 때 `QUICK_GUIDES`와 `TRACK_GUIDES`도 함께 갱신합니다.

아래 파일은 직접 편집하지 않고 생성 결과를 커밋합니다.

```text
README.md
index.html
```

`README.md`와 `index.html` 상단의 문제 신호별 빠른 길찾기, 심화 트랙 지도, 카드 배지 기준도 `scripts/generate_catalog.py`에서 생성됩니다. 새 허브 레슨을 추가하거나 기존 허브의 역할이 바뀌면 `QUICK_GUIDES`, `TRACK_GUIDES`, `METADATA_GUIDE`가 현재 학습 경로와 맞는지 함께 확인합니다.

새 레슨을 처음 작성할 때는 `templates/lesson.md`를 출발점으로 사용할 수 있습니다.

## lessonId 규칙

lessonId는 소문자 영어와 하이픈을 사용합니다.

좋은 예:

```text
zero-one-bfs
topological-sort
binary-lifting
```

피해야 할 예:

```text
ZeroOneBFS
0_1_BFS
한글-레슨
```

## 레슨 작성 스타일

직접 풀이 트랙(`heuristic-notes`)의 새 제출 예제는 h-contest 함수 구현형 `user.cpp`를 기준으로 작성합니다. STL과 표준 헤더를 쓰지 않고, 공개 API·고정 배열·직접 구현을 기본으로 합니다. `struct`, 참조, `template`는 사용 가능합니다. 일반 C++/STL이 필요한 참고 예제와 로컬 테스트 하네스는 적용 환경을 명시합니다. 기존 레슨의 전환은 ROADMAP 순서로 진행합니다.

배열·난수·정렬·큐·힙의 공통 코드는 [실전 C++ 기본기와 공통 코드](lessons/cpp-contest-basics/lesson.md)를 원문으로 사용합니다. 문제별 예제에는 필요한 블록 이름, 배열 상한, 인덱스 범위, TC 초기화 위치를 함께 적습니다. 설명 없이 거대한 템플릿을 전부 복사시키지 않습니다. 새 공통 코드가 필요하면 실제 사용 문제와 경계 검증을 함께 추가합니다.

이 레슨의 `cpp compile-check snippet=<name>` 블록은 `python3 scripts/check_cpp_basics.py`가 직접 추출하여 실행 검증합니다. 전체 validator에서도 호출하므로 C++17 컴파일러와 ASan/UBSan 지원이 필요합니다. 독립적으로 복사할 블록은 다른 블록에 대한 숨은 의존성을 두지 않습니다. 제출 소스에는 테스트 하네스의 헤더와 `main`을 넣지 않습니다.

문제 상황에서 시작해 작은 예시로 원리를 설명하고, 필요한 구현과 비용으로 이어갑니다. 모든 강의에 같은 목차를 맞추지 않습니다. 하위 페이지 목록을 썼다면 같은 링크를 나열하는 학습 순서를 다시 붙이지 않습니다.

예시는 새로운 풀이 판단, 상태 변화, 반례, 구현상의 차이 중 무엇을 설명하는지 분명해야 합니다. 이름만 나열한 응용, 한 줄 연산을 감싼 함수, 핵심 판정·전이를 비워 둔 프레임워크는 넣지 않습니다. 빠른 풀이와 기준 풀이가 같은 함수를 호출하는 비교 코드는 검증 예시가 아닙니다.

같은 구현을 부분 코드와 전체 코드로 반복하지 않습니다. 한 곳의 구현을 설명하고, 다른 레슨에서는 링크와 달라지는 조건만 둡니다. 대안 구현은 적용 조건이나 성능 차이를 설명할 때만 남깁니다. 삭제 후 독립적으로 읽을 내용이 부족한 페이지는 관련 본문에 합치고 manifest와 소개 문구를 맞춥니다.

조건과 주의점은 그 조건이 쓰이는 설명이나 코드 옆에 둡니다. 본문에서 설명한 내용을 결론, 실수 표, 체크리스트로 바꿔 반복하지 않습니다. 체크리스트는 검증 절차 자체를 가르치거나 서로 다른 조건을 실제로 비교해야 할 때만 사용합니다.

설명이 끝나면 그 자리에서 마칩니다. “핵심을 기억하자”, “문제 조건을 잘 확인하자”, “이 도구가 모든 문제의 정답은 아니다” 같은 일반론으로 결론 분량을 채우지 않습니다. 이어지는 문제가 있다면 문제를 먼저 소개하고 무엇을 구현하거나 비교할지 적습니다.

고급 레슨은 정의와 식만으로 끝내지 말고, 아래 중 최소 하나를 포함하는 것을 권장합니다.

- 손으로 따라갈 수 있는 작은 예시 또는 상태 변화 trace
- 왜 조건이 필요한지 보여 주는 반례
- 이 기법을 쓰지 말아야 하는 경우
- 좌표, 그래프, DP 상태 전이가 헷갈리는 주제의 간단한 도식

레슨 제목은 `lessons.json`의 `title`과 `lesson.md`의 H1이 정확히 같아야 합니다. 본문은 한국어 설명을 기본으로 하되, 통용되는 영어 용어는 처음 등장할 때 함께 적어도 됩니다.

h-contest 문제 링크를 넣을 때는 `/practice/<PROBLEM_ID>` 형식을 사용합니다. 운영 화면에서는 h-contest에 로그인한 사용자에게만 이 링크가 실제 문제 진입 링크로 활성화됩니다.

연습은 실제 문제 또는 입력·과제·확인 방법이 갖춰진 로컬 연습만 싣습니다. 본문 중간의 문제 링크, 짧은 문단, 목록도 사용할 수 있으며, 별도 연습 절이나 입문·표준·응용·함정 네 단계 표는 필수가 아닙니다. 관련성이 약한 문제를 분량을 채우기 위해 연결하지 않습니다.

아직 준비하지 못한 연습과 본문 보강 항목은 [ROADMAP.md](ROADMAP.md)에 둡니다. 강의 본문에 `TODO` 행이나 빈 연습 페이지를 만들지 않습니다. `practiceStatus`는 실제 내용에 맞춰 `none`/`todo`/`linked`/`verified`로 표시하며, 예정 항목만 있는 강의를 `linked`로 표시하지 않습니다.

validator는 목차나 표 형식을 강제하지 않습니다. 기본·심화와 참고 노트의 모든 강의에서 본문의 `TODO`와 근거 없는 `linked`/`verified` 표시를 검사합니다. 미완성 연습 후보는 ROADMAP에 보관하고, 실제 연습이 없는 강의를 `linked`로 표시하지 않습니다.

C++ 코드 블록은 기본적으로 문법을 직접 확인합니다. 독립 translation unit으로 컴파일 가능한 예제는 fence에 `compile-check`를 붙이면 validator가 `c++ -std=c++17 -fsyntax-only`로 검사합니다.

````markdown
```cpp compile-check
long long square(int value) {
    return 1LL * value * value;
}
```
````

## PR 전에 확인할 것

- `lessons/<lessonId>/lesson.md`를 추가하거나 수정했나요?
- `lessons.json`의 title, description, summary, order, folderId, level, estimatedMinutes, prerequisites, nextLessons, relatedLessons, tags, pages를 갱신했나요?
- `python3 scripts/generate_catalog.py`를 실행했나요?
- `python3 scripts/validate_lessons.py`를 실행했나요?
- `lesson.md`의 H1 제목과 `lessons.json`의 title이 일치하나요?
- 이미지와 내부 링크가 깨지지 않나요?
- C++ 코드는 문법상 문제가 없나요?
- 미완성 연습은 본문 대신 `ROADMAP.md`에 남겼나요?
- 결론·체크리스트가 본문을 반복하거나 일반론으로 분량을 채우지 않나요?
- `lessonType`, `practiceStatus`, `implementationStatus`가 실제 문서 완성도와 맞나요?
- `difficultyAxes`가 레슨의 어려운 이유를 정확히 설명하나요?
- 새 허브나 트랙 역할이 생겼다면 생성 카탈로그의 빠른 길찾기와 트랙 지도도 맞게 갱신했나요?

공통 구현을 참조하는 예제는 의존 본문의 정의를 먼저 붙인다고 명시합니다. `scripts/review-example-cases.json`은 실제 Markdown 블록을 조합하고 `scripts/check_review_examples.py`로 경계·단순 풀이 비교를 실행합니다. 전체 validator에도 포함되어 있습니다. 전체 재검토 기록은 [LESSON_REVIEW.md](LESSON_REVIEW.md)에 남깁니다.
