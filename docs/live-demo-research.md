# 실제 데모 조사와 검토 화면 재구성

조사일: 2026-10-29. [트레져러 AI 개발자 인턴 공고](https://treasurer.recruit.roundhr.com/c/nLeVw9amBH)의 금융 문서 파싱·출처, 수치/문맥 검사, 평가, MCP 도구 실행을 기준으로 조사했다. 앞선 [제품·도움말 조사](ui-research.md)에 이어, 이번에는 다른 개발자가 공개한 **실제 작업 화면과 샘플 동작**을 우선 확인했다.

사용자는 배경을 포함한 화면 전체가 전형적인 AI 데모처럼 보인다고 지적했다. 처음에는 배경색 교체로 해석해 짙은 외곽색을 시험했으나, 그것으로 해결되지 않는 요구임을 확인하고 해당 시안은 배포하지 않았다. 이번 변경은 자료를 고르고 검토를 끝내는 흐름까지 포함한다.

## 실제로 확인한 범위

공개 데모 주소 11곳에 접근을 시도했다. 그중 6곳은 첫 화면을 확인했고, **2곳에서는 제공된 샘플의 작업 화면까지 직접 조작했다.** 로그인·보안 검증·인증서 오류로 열리지 않은 서비스는 UI를 확인한 것으로 세지 않았다. 외부 서비스에 파일을 업로드하거나 유료 API를 실행하지 않았다. 제품의 실제 고객 운영 여부나 신뢰도는 이 조사로 검증하지 않았다.

|대상|확인 수준과 관찰|이번 구현에 적용한 판단|
|---|---|---|
|[Alan Salomon Invoice Extraction](https://demo.alansalomon.ai/) · [프로젝트 설명](https://alansalomon.ai/work/invoice-extraction)|실제 문서 목록과 공개 sample 상세를 확인. `sample-invoice-with-an-error.pdf`에서 합계 불일치 항목을 눌러 PDF의 해당 합계가 강조되는 것을 확인. subtotal 100319.27 + tax 19060.66과 total 119479.93의 차이를 항목 옆에 표시.|가장 직접적인 작업 흐름 참고. 문서·항목·검토 사유를 같은 화면에 두고, 선택한 숫자와 근거 위치를 동기화. 외부 데모의 Approve 버튼을 자동 판정과 혼동하지 않도록 우리 앱은 **개인 확인 표시**로 한정.|
|[Intake AI](https://intake.stevenmallqui.com/) · [코드](https://github.com/smallqui/intake-ai)|REAL API가 꺼진 기본 상태에서 Simple Receipt 샘플 선택. Tech Bistro & Cafe, 42.50, 4개 행과 문서 이력·추출 필드·내보내기 작업 화면 확인. 실제 모델 호출을 검증한 것은 아님.|자료 목록, 작업 대상, 결과 내보내기를 연결. 큰 소개 문구, 시간·비용 절감 추정 배지, 어두운 장식은 채택하지 않음.|
|[Document Intelligence Platform](https://document-intelligence-platform-bice.vercel.app/) · [코드](https://github.com/ryuk7728/document-intelligence-platform)|실제 첫 화면과 문서 유형·업로드·이력 영역 확인. 이력은 로딩 상태. 파일 제출과 분석 결과는 시험하지 않음.|범위와 입력 제약의 명시는 참고. 큰 그라데이션 소개 영역, 구현하지 않은 업로드를 흉내 내는 방식은 제외.|
|[Ethan Haas Verifiable Extraction](https://ethanhaas.dev/demo/)|초기 화면에서 재무 보고서 예제 4개, PDF.js 영역, 숫자 검산, 전치 오류 주입 설명을 확인. 재방문 후 예제 버튼 조작은 timeout으로 완료되지 않음.|수치 검사 이유를 노출하는 접근 참고. 오류 주입을 직접 검증했다고 주장하지 않음. KPI/소개 화면 구성은 채택하지 않음.|
|[IRIS demo](https://demo.iriscorporate.com/en/)|공개 첫 화면과 여러 문서 처리 데모 선택 확인. 동의 창을 닫았으나 실제 분석 작업은 완료하지 않음.|문서 처리 목적별 구분만 참고. 실제 작업 UI를 검증한 사례로 사용하지 않음.|
|[Apryse showcase](https://showcase.apryse.com/)|첫 화면, Text & Data Extraction의 9개 메뉴를 펼쳐 확인. 뷰어는 대기 상태에 머물러 원문 렌더링은 확인하지 못함.|보기/추출 작업 구분만 참고. PDF 렌더링 성공 근거로 사용하지 않음.|
|[Paperless-ngx public demo](https://demo.paperless-ngx.com/)|Cloudflare 보안 확인으로 차단.|확인 불가. 우회하지 않음.|
|[DocumentCloud](https://www.documentcloud.org/)|Cloudflare 보안 확인으로 차단.|확인 불가.|
|[Docling](https://www.ibm.com/granite/docs/models/docling)|공식 설명을 확인했으나 접근한 Hugging Face 앱 주소는 404.|동작하는 데모로 세지 않음.|
|[Document Intelligence / abhati27](https://github.com/abhati27/document-intelligence)|README 확인. 연결된 Streamlit 앱은 브라우저 인증서 오류로 열리지 않음.|소스 소개만 확인, 화면 평가 제외.|
|[Azure Document Intelligence Studio](https://documentintelligence.ai.azure.com/studio)|브라우저 연결/인증서 오류로 열리지 않음.|UI 검증 제외.|

조사 브라우저의 인증서 신뢰 문제 때문에 일부 페이지는 기본 TLS 검증을 사용하는 HTTP 클라이언트 경유로 열었다. TLS 검증을 끄거나 보안 확인 페이지를 우회하지 않았다. 샘플 버튼으로 접근 가능한 공개 예시만 사용했으며 공유 데모의 삭제·승인·재분석 작업은 실행하지 않았다.

## SK Family와 공식 디자인 자료

[SKN27-FINAL-1Team](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN27-FINAL-1Team)과 [SKN27-FINAL-3Team](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN27-FINAL-3Team)의 현재 README도 다시 확인했다. 1Team은 영수증·냉장고 서비스와 기능/MCP 영상 링크, 3Team은 교통사고 분석과 파일럿 배포 설명을 제공한다. 이번 확인에서는 직접 사용할 공개 앱 주소를 확보하지 못했고, 영상 재생을 완료했다고 주장하지 않는다. README의 문제·동작·검증 근거를 구분하는 구성은 프로젝트 설명에 참고했다. 조직 내 다른 프로젝트를 포함한 앞선 조사 범위는 [프로젝트 조사](research.md)에 별도로 기록했다.

배경 재검토 과정에서는 [Carbon](https://carbondesignsystem.com/elements/color/overview/), [Spectrum](https://spectrum.adobe.com/page/color-system/), [Atlassian](https://atlassian.design/foundations/color/), [Primer](https://primer.style/foundations/color), [Radix](https://www.radix-ui.com/colors), Linear의 UI 개편, Quartr·DataSnipper·ARIA의 공식 화면도 살펴봤다. 이들은 실제 업무 데모와 구분되는 디자인 참고다. 특정 팔레트를 적용했다는 이유만으로 출시 제품 수준을 달성했다고 판단하지 않는다.

## 최종 반영

|이전 화면의 문제|현재 동작|
|---|---|
|화면 제목·종이 모양·색상이 업무보다 먼저 보임|작은 상단 메뉴와 실제 보고서 목록. 중립적인 작업 배경, 흰 데이터 영역, 선택/작업에 쓰는 파란색. 가짜 PDF 활자·장식 영문 제거.|
|A/B의 모든 설정이 항상 펼쳐져 있음|현재 비교 조건을 요약하고 상세 설정은 접어 둠. A/B 각각의 기간·연결 범위·통화는 요약에서도 구분.|
|수치를 보는 데서 체험이 끝남|보고서 선택 → 항목과 근거 대조 → 개인 메모·확인 표시 → CSV 내보내기.|
|상태가 성공 배지로만 읽힐 수 있음|자동 문맥 판정과 개인 확인은 별개. 개인 확인을 눌러도 기간/범위/통화 불일치의 계산 차단은 유지.|
|한 번 만든 결과와 현재 실행이 혼동될 수 있음|설정 변경/실행 중에는 이전 결과·내보내기 비활성화. 실제 MCP 실행 기록은 별도 상세.|
|작은 화면에서 A/B를 번갈아 찾아야 함|모바일에서는 항목별 두 금액을 함께 표시. 숫자 선택 시 근거로 이동. 원문 표의 가로 스크롤은 해당 표 안에 제한.|

실제로 수집한 삼성전자 보고서 2건만 목록에 둔다. 업로드·계정·팀 협업·여러 기업 지원을 보여주기 위한 가짜 버튼은 추가하지 않았다. 근거표는 **수집 값의 재구성**임을 명시하고 발행사 PDF를 별도로 제공한다. 외부 PDF 렌더링 성공을 보장하지 않는다.

메모는 fact ID·문서 해시·A/B 순서·비교 방식에 묶여 **현재 브라우저의 localStorage에만** 저장된다. 다른 기기나 팀원에게 동기화되지 않는다. 저장 실패 시 실패를 표시하고 현재 탭에 초안을 유지해 CSV로 보관할 수 있게 했다. 기존 메모를 읽지 못하면 빈 기록으로 덮어쓰지 않도록 편집과 CSV를 제한하고 재시도를 제공한다. 독립 AI 리뷰가 지적한 읽기 실패 처리를 수정하고 회귀 검사에 추가했다. CSV에는 원 수치·기간·범위·단위·출처·자동 판정·개인 확인·메모를 구분해 담으며, 텍스트가 스프레드시트 수식으로 해석되지 않도록 처리한다.

## 확인 방법

- Python 단위·통합 검사 54개: 기존 문서·수치·MCP·API 보장 유지.
- Node 검사 5개: 검토 문맥 분리, 저장 데이터 검증, 저장 실패, CSV 내용과 수식 방어.
- Playwright PC/모바일 37개: 기존 흐름 및 문서 선택, 새로고침 후 메모/확인 유지, 조건별 메모 분리, 개인 확인과 자동 판정 분리, 실제 CSV, 저장 실패 복구.
- 현재 실행 결과: [브라우저 검사](../artifacts/browser-check.json). 공개 배포 확인은 v1.2.0 릴리스에 별도 기록한다.

이 검사는 기능과 표시의 확인이지, 사용성 조사나 사용자 선호 검증을 대신하지 않는다.


## v1.2.1 · 선택한 배경 방향 반영

사용자가 후속 배경 후보 비교에서 **1번 Ramp Accounting**을 선택했다. 참고 자료는 [Ramp 공식 회계 안내](https://support.ramp.com/overview-of-ramp-accounting/)와 해당 페이지의 [작업 화면](https://assets.ramp.com/help-center/overview-of-ramp-accounting/attachments/24379722094739.gif)이다. 이미지 바깥의 녹색 연출 배경은 앱 내부 배경으로 가져오지 않는다.

작은 표시 변경으로 범위를 한정했다. 흰색의 연속된 본문, 옅은 중성 회색 문서 목록, 넓은 왼쪽 비교표와 오른쪽 근거 영역, 얇은 구분선을 사용한다. 패널의 외곽 테두리·모서리·틈과 청회색 바탕을 없애고, 선택 상태는 중성 명도 차이와 밑줄로 표시한다. 검색·검증 기록 화면도 같은 표면 규칙을 적용한다. 로고·고유 아이콘·화면 자산을 복제하지 않는다.

계산·MCP·메모·CSV 동작은 변경하지 않는다. 기존 37개 브라우저 흐름으로 근거 선택, 키보드, 메모와 실패 복구, CSV, 모바일을 확인하고 PC/모바일 화면과 대표 텍스트 대비를 살핀다. 배포 결과는 v1.2.1 릴리스에 기록한다.
