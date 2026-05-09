# /harness-check

Claude Code 하네스 전체 설정을 수집·분석하고, `~/Vaults/workspace-map/workspace_map.md`의 `<!-- AUTO:START -->` ~ `<!-- AUTO:END -->` 구간을 최신 상태로 덮어쓴다.

## 읽어야 할 소스 (전부, 누락 없이)

1. `~/.claude/settings.json` — model, language, effortLevel, advisorModel, env, permissions(allow/deny), enabledPlugins, extraKnownMarketplaces, 기타 모든 키
2. `~/.claude/settings.local.json` — 로컬 오버라이드
3. `~/.claude/hooks/` — 각 스크립트 전체 읽기 (로직 요약 포함)
4. `~/.claude/skills/` — 설치된 스킬 전체 목록
5. `~/.claude/agents/*.md` — 각 에이전트 frontmatter (name, description, model, color)
6. `~/.claude/commands/*.md` — 각 커맨드 첫 줄 설명
7. `~/.claude/knowledge/index.md` — KB 인덱스 항목 수 및 현황
8. `~/.claude/CLAUDE.md` — 글로벌 지침 전체
9. `~/CLAUDE.md` — 루트 프로젝트 지침 전체
10. `settings.json`의 `hooks` 필드 — 이벤트별 matcher + command

## 실행해야 할 점검 (수집과 병행)

### A. 훅 스크립트 건강 상태

```bash
# 1. 문법 검사
for f in ~/.claude/hooks/*.py; do
    uv run python3 -m py_compile "$f" 2>&1 && echo "✅ $(basename $f)" || echo "❌ $(basename $f)"
done

# 2. 의존성 바이너리 존재 확인
which agent-notify mempalace ruff 2>/dev/null

# 3. guards/ 패키지 임포트
uv run python3 -c "import sys; sys.path.insert(0,'$HOME/.claude/hooks'); from guards import bash,files,mcp_github,mcp_playwright,web; print('✅ guards/')"

# 4. context_inject.py 실제 실행 테스트
echo '{}' | uv run python3 ~/.claude/hooks/context_inject.py
```

### B. 플러그인 30일 사용 빈도 (JSONL 파싱)

```python
# ~/.claude/projects/**/*.jsonl 에서 "skill" 키 추출, 30일 이내 파일만
import json, os, glob, re
from datetime import datetime, timedelta
from collections import Counter

cutoff = datetime.now() - timedelta(days=30)
skill_calls = Counter()
pattern = re.compile(r'"skill"\s*:\s*"([^"]+)"')

for jsonl in glob.glob(os.path.expanduser("~/.claude/projects/**/*.jsonl"), recursive=True):
    if datetime.fromtimestamp(os.path.getmtime(jsonl)) < cutoff:
        continue
    try:
        content = open(jsonl).read()
        for m in pattern.finditer(content):
            skill_calls[m.group(1)] += 1
    except:
        pass

# 상위 15개 + 0회 플러그인 교차 출력
```

### C. MCP 프로세스 중복 감지

```bash
ps aux | grep -E "(playwright|firecrawl|context7|github|mempalace|brave|duckdb)" \
  | grep -v grep \
  | awk '{for(i=11;i<=NF;i++) printf $i" "; print ""}' \
  | grep -oE '(playwright|firecrawl|context7|github|mempalace|brave|duckdb)' \
  | sort | uniq -c | sort -rn
```

1 초과이면 중복 경고.

### D. 프로젝트 state 상위 5

```python
# ~/.claude/projects/ 디렉터리별 JSONL 총 크기 + 마지막 활성일
# 크기 내림차순 상위 5개 출력
```

## AUTO 구간에 생성할 내용

아래 구조로 마크다운을 작성한다. 갱신 타임스탬프 포함.

```
## 🔀 Hook Event Pipeline

(mermaid flowchart LR — 각 이벤트를 노드로 연결)
- settings.json의 hooks에서 이벤트 순서대로 노드 생성
- 각 노드: 이벤트명 + 스크립트명 + [매처] 표시
- 색상: SessionStart=#4ade80, UserPromptSubmit=#60a5fa, PreToolUse=#f97316,
  PostToolUse=#a78bfa, Stop=#f43f5e, PreCompact=#fbbf24, SessionEnd=#94a3b8
- style로 fill/stroke/color 지정 (dark theme용 어두운 fill)

## 🔬 Research Workflow Pipeline

(mermaid flowchart LR — Athena 연구 파이프라인)
- /ingest → /solve → /visualize → /draft → /ppt
- 각 노드에 슬래시 커맨드명 + 한줄 설명
- 색상: ingest=#4ade80, solve=#60a5fa, visualize=#a78bfa, draft=#fbbf24, ppt=#f97316

## 하네스 전체 스냅샷
_자동 갱신: YYYY-MM-DD — /harness-check_

### ⚙️ 설정 핵심값
- model / advisorModel / effortLevel / language / defaultMode
- env 변수
- permissions allow 목록 (한 줄)
- permissions deny 목록 (한 줄)
- settings.local.json 오버라이드 (없으면 "없음 ✅")
- cleanupPeriodDays, 기타 불리언 플래그

### 🔌 플러그인 & 마켓플레이스
- enabledPlugins 표 (플러그인 | 마켓 | 상태 | 30일 호출수)
- extraKnownMarketplaces 한 줄

### 🪝 훅 파이프라인
이벤트 | 매처 | 스크립트 | 로직 요약
(각 스크립트를 실제로 읽고 1~2줄 요약)
고아 스크립트 (hooks/ 에 있지만 settings.json 미연결) 명시

### 📦 스킬
전체 목록 한 줄 (gstack 등 특이사항 괄호 표기)

### 🤖 에이전트
이름 | 모델 | 역할 요약

### 🌐 커맨드
이름 | 설명

### 📚 Knowledge Base
index.md 항목 수, daily 로그 경로, compile 상태, 로드 방식

### 📋 CLAUDE.md 레이어
- global: 섹션 목록
- project: 섹션 목록

### 🏥 훅 건강 상태
(점검 A 결과)
스크립트 | 문법 | 비고
의존성: agent-notify / mempalace / ruff — 설치 여부
guards/ 패키지 — 임포트 성공 여부

### 📊 플러그인 사용 빈도 (30일)
(점검 B 결과)
플러그인 | 30일 호출 — 0회이면 🟡 표시

### 🔄 MCP 프로세스 현황
(점검 C 결과)
MCP | 프로세스 수 — 1 초과이면 🔴 중복 경고

### 💾 프로젝트 State 상위 5
(점검 D 결과)
프로젝트 | 마지막 활성 | 세션 수 | 크기

### 🔍 진단
수집한 정보를 바탕으로 아래 항목을 분석해 표로 출력:
항목 | 유형 | 내용

유형:
- 🔴 오류: matcher 누락, 스크립트 경로 깨짐, 잘못된 이벤트명
- 🟠 중복: 동일하거나 겹치는 스킬/에이전트/커맨드, MCP 중복 프로세스
- 🟡 주의: 잠재적 위험, 설계 개선 여지, 0회 플러그인
- 🟢 정보: 의도된 설계이지만 오해 소지 있는 것
- ✅ 이상 없음: 전체 이상 없을 경우 한 줄로 명시

진단 기준:
- 고아 스크립트 (hooks/ 에 있으나 settings.json 미등록)
- settings 레이어 간 충돌
- 훅 파이프라인 순서/누락/중복 동작
- 미사용·중복·효과 없는 항목 (30일 0회 플러그인 포함)
- skipDangerousModePermissionPrompt 등 위험 플래그
- MCP 중복 프로세스
- 현재 Claude Code 기능 대비 구식 패턴
- 훅 스크립트 문법/실행 오류
```

## 주의

- AUTO 구간(`<!-- AUTO:START -->` ~ `<!-- AUTO:END -->`) 만 덮어쓴다. 그 밖의 내용은 건드리지 않는다.
- 마커가 없으면 파일 끝에 마커와 함께 추가한다.
- 진단까지 전부 AUTO 구간 안에 포함한다. 별도 섹션 생성 금지.

## workspace_map.md 갱신 후 자동 커밋 + diff 요약

`workspace_map.md` 수정 완료 후 순서대로 실행한다:

```bash
# 1. 변경 통계 출력 (커밋 전)
git -C ~/Vaults/workspace-map diff --stat HEAD -- workspace_map.md

# 2. 커밋
git -C ~/Vaults/workspace-map add workspace_map.md && git -C ~/Vaults/workspace-map commit -m "harness-check: $(date +%Y-%m-%d) 자동 갱신"
```

`--stat` 출력을 그대로 사용자에게 보여준다. 변경 없으면 커밋 없이 종료한다.

## HTML 대시보드 갱신

`workspace_map.md` 갱신 후, 대시보드도 재생성한다:

```bash
uv run python3 ~/Vaults/workspace-map/gen_dashboard.py
```

`--open` 플래그는 붙이지 않는다 (자동으로 브라우저 열 필요 없음).
