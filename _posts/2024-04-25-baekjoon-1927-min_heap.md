---
title:  "백준 1927-최소힙"
excerpt: "md 파일에 마크다운 문법으로 작성하여 Github 원격 저장소에 업로드 해보자. 에디터는 Visual Studio code 사용! 로컬 서버에서 확인도 해보자. "

categories:
  - Blog
tags:
  - [Blog, jekyll, Github, Git, baekjoon]

toc: true
toc_sticky: true
 
date: 2024-04-25
last_modified_at: 2024-04-25
---

2024-4-35에 백준 1927-최소힙 문제를 풀었다

https://www.acmicpc.net/problem/1927

![image](https://github.com/softkleenex/softkleenex.github.io/assets/92619941/e71e63ee-850f-45a9-a36f-99a5e5c58ea5)


체출한 소스코드는 다음과 같다.

```c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#define swap(a, b) do{int temp = a; a = b; b = temp;}while(0)

int heap[100000];
int size = 0;



int parent(int index)
{ 
    return (index -1) /2;
}

int leftChild(int index)
{ 
    return (index)*2 +1;
}

int rightChild(int index)
{ 
    return (index)*2 + 2;
}


void insert(int value)
{
    if (size == 9999)
    {}    //힙이 꽉 찼다
    
    int index = size;
    heap[size] = value;
    size ++;
    
    while ((index != 0) && (heap[parent(index)] > heap[index]))
    {
        swap(heap[index], heap[parent(index)]);
        index = parent(index);
    }
}




void minHeapify(int index)
{
    int left = leftChild(index);
    int right = rightChild(index);
    int smallest = index;

    if (left < size && heap[left] < heap[smallest])
        smallest = left;
    if(right < size && heap[right] < heap[smallest])
        smallest = right;
    
    if (smallest != index)
    { 
        swap(heap[index], heap[smallest]);
        minHeapify(smallest);
    }

}

int removeMin()
{
    if (size <= 0)
        return 0;
    
    if (size == 1)
    {
        size -= 1;
        return heap[0];
    }

    int root = heap[0];
    heap[0] = heap[size -1];
    size -= 1;
    minHeapify(0);

    return root;

}




int main()
{
int n = 0;
scanf("%d", &n);



int* arr2 = malloc(sizeof(int) * (size_t)n);

for(int a = 0; a < n; a ++)
{
    scanf("%d", &arr2[a]);
}

for(int a = 0; a < n; a++)
{
int x = 0;
x = arr2[a]; 
//0 입력시 배열의 최소값 출럭, 그 배열 제거 
// 자연수 입력시에 배열에 그 값 넣음

    if(x == 0)
    {
        if(size == 0) //인덱스가 0 >> 즉, 배열이 아예 비워져 있는 경우
            printf("0\n");
        else//배열에 뭐라도 있는 경우
        {   
            printf("%d\n", heap[0]);
            removeMin();
        }
    }
    if(x > 0)
    {
       insert(x);
    }
}


return 0;

}
```

문제의 시간 제한을 생각하면, 이는 자료구조의 힙을 이용하여 풀어야 한다. 
코드 설명이 주석으로 들어간 코드를 첨부한다

```C

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#define swap(a, b) do{int temp = a; a = b; b = temp;}while(0)

int heap[100000];
int size = 0;

//size >> 배열의 가용 인덱스이다. 비워져있을떄는 0, 값이 하나 있으면 1, 둘 있으면 2......
//배열의 최대 길이는 x의 이하이다.
//배열의 활용 인덱스는 0에서부터



int parent(int index)
{ 
    return (index -1) /2;
}

int leftChild(int index)
{ 
    return (index)*2 +1;
}

int rightChild(int index)
{ 
    return (index)*2 + 2;
}

//인덱스 0부터 시작하는 배열-힙은 parent*2 + 1 > leftchild, parent*2+2 > right chlide,이다. 
//(leftchild || right chlild)-1 /2 > parent이다. 

void insert(int value)//힙에 새로운 값을 넣을떄이다.
{
    if (size == 9999)
    {}    //힙이 꽉 찼다
    
    //size가 9999(즉, heap의 크기 -1)이라는것은, 힙이 꽉 찼다는것이다. 즉, 입력을 받지 않고 넘어간다.


    int index = size;
    heap[size] = value;
    size ++;

   //index에는 insert하기 전의 size, size에는 insert한 후의 size가 들어있다.
   //insert를 index에 부분에 하였으니 - heap의 가장 끝 부분에 넣었으니- index에서부터 위로 올라가면서 최소힙을 만족하는지 검사한다.
   //index를 별도로 선언한 이유는, 검사단계에서 size를 번형해야하므로, index를 별도로 선언하여 index에 size를 넣었다

    while ((index != 0) && (heap[parent(index)] > heap[index])) //검사가 끝나지 않았으며 -index가 root가 아니며 - and 
										    //index와 index의 parent가 최소힙 조건에 맞는 경우에 검사한다 
    {
        swap(heap[index], heap[parent(index)]); //while문을 통과한 상태이므로 index의 값과 그 parent의 값은 바뀌어야 하고
        index = parent(index);//index를 그 parent로 바꾸어서 검사를 계속한다.
    }


}


//remove후에 최소힙 조건을 유지하기 위해 선언한 함수 - remove보다 위에 있어야한다!

void minHeapify(int index)
{
    int left = leftChild(index);
    int right = rightChild(index);
    int smallest = index;

    if (left < size && heap[left] < heap[smallest])
        smallest = left;
    if(right < size && heap[right] < heap[smallest])
        smallest = right;


//right <size, left<size를 통해서 right와 left가 heap의 범위에 들어와 있을떄만 생각한다.

//위의 조건문들을 통해, index와 그 right, left의 값들중 smallest한것이 smallest에 들어가 있다.
    
    if (smallest != index)//index가 smallest가 아닌경우 - 즉, 최소힙을 만족시키지 않는 경우에
    { 
        swap(heap[index], heap[smallest]); //smallest와, index의 값을 뒤바꾸고,
        minHeapify(smallest);//재귀적으로 뒤바꾼 그 값에 대해 minHeapify를 시행한다. 
    }

}

//heap의 최소를 제거하는 함수-최소힙이므로, 힙의 가장 위-배열의 인덱스0을 제거하게된다.

int removeMin()
{
    if (size <= 0)
        return 0;
    //size가 0 이하 > 음수는 오류의 경우이고, 0인경우는 힙에 아무것도 없다는것이다    

    if (size == 1)
    {
        size -= 1;
        return heap[0];
    }

   //size가 1>heap에 값이 하나만 있다는것, heap[0]이 그 유일한 값이므로 size -=1 을 하고 heap[0]을 리턴한다

    int root = heap[0];
    heap[0] = heap[size -1];
    size -= 1;
    minHeapify(0);
    return root;

//그 외의 경우 > heap[0]을 리턴하고, heap의 가장 끝 값을 heap[0]으로 가져오고, size -= 1을 하고, 0 에서부터 minheapify를 시행한다.
 
}




int main()
{
int n = 0;
scanf("%d", &n);



int* arr2 = malloc(sizeof(int) * (size_t)n);

for(int a = 0; a < n; a ++)
{
    scanf("%d", &arr2[a]);
}

for(int a = 0; a < n; a++)
{
int x = 0;
x = arr2[a]; 
//0 입력시 배열의 최소값 출럭, 그 배열 제거 
// 자연수 입력시에 배열에 그 값 넣음

    if(x == 0)
    {
        if(size == 0) //인덱스가 0 >> 즉, 배열이 아예 비워져 있는 경우
            printf("0\n");
        else//배열에 뭐라도 있는 경우
        {   
            printf("%d\n", heap[0]);
            removeMin();
        }
    }
    if(x > 0)
    {
       insert(x);
    }
}


return 0;

}
```

end