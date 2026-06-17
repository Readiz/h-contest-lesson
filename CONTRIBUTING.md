# Contributing

h-contest-lesson 저장소는 h-contest 알고리즘 레슨 콘텐츠의 source of truth입니다.

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

## 레슨 수정 방법

기존 레슨은 아래 파일을 수정합니다.

```text
lessons/<lessonId>/lesson.md
```

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

이미지가 필요하면 아래 디렉터리에 추가합니다.

```text
lessons/<new-lesson-id>/lesson-assets/
```

그다음 아래 명령으로 파생 파일을 갱신하고 검증합니다.

```bash
python3 scripts/generate_catalog.py
python3 scripts/validate_lessons.py
```

아래 파일은 직접 편집하지 않고 생성 결과를 커밋합니다.

```text
README.md
index.html
```

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

각 레슨은 가능하면 아래 흐름을 따릅니다.

1. 언제 이 개념이 필요한가
2. 핵심 아이디어
3. 작은 예시
4. C++ 구현
5. 시간 복잡도
6. 자주 하는 실수
7. 문제를 볼 때 체크할 조건

## PR 전에 확인할 것

- `lessons/<lessonId>/lesson.md`를 추가하거나 수정했나요?
- `lessons.json`의 title, description, summary, order, tags를 갱신했나요?
- `python3 scripts/generate_catalog.py`를 실행했나요?
- `python3 scripts/validate_lessons.py`를 실행했나요?
- `lesson.md`의 H1 제목과 `lessons.json`의 title이 일치하나요?
- 이미지와 내부 링크가 깨지지 않나요?
- C++ 코드는 문법상 문제가 없나요?
