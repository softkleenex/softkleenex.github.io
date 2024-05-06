---
published: false
---

깃허브계정아이디.github.io 폴더 내의 현재 변동 사항은

_post 폴더가 새로 생김.
그 속에 포스트 .md 파일이 새로 생김.

이다. 이를 git push 해주어 Github Pages 원격 서버에 올려주어야 한다. 그럼 이제 내 블로그 페이지에 포스트가 올라온 것을 확인할 수 있을 것이다.





git이 미리 설치되어 있어야 한다.

git bash로 일일이 git add, commit, push 명령어를 칠 필요 없이 VS code UI로 Github 원격 서버에 포스트를 업로드 할 수 있다.
작업 중인 이 폴더는 이미 git과 연결되어 있는 폴더이기 때문에 그냥 VS code 왼쪽 상단 세번째 아이콘을 클릭하면 바로 git을 사용할 수 있다.


모든 변경 내용 스테이징을 누르고 (= git add .)

![image](https://github.com/softkleenex/softkleenex.github.io/assets/92619941/c96be902-b974-4f8e-918e-79c85e2744fd)

커밋메세지를 쓴 후 체크 표시를 누르면 커밋 된다. (= git commit -m “블라블라”)
그리고 체크 표시 옆에 …를 눌러 푸시 (= git push) 해주면 블로그에 포스트가 잘 업로드 될 것이다. 최소 1분 정도는 기다려주어야 하는 것 같다. ?