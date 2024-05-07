---
title:  "ë°±ì?? 1927-ìµœì†Œ?™"
excerpt: "md ?ŒŒ?¼?— ë§ˆí¬?‹¤?š´ ë¬¸ë²•?œ¼ë¡? ?‘?„±?•˜?—¬ Github ?›ê²? ????¥?†Œ?— ?—…ë¡œë“œ ?•´ë³´ì. ?—?””?„°?Š” Visual Studio code ?‚¬?š©! ë¡œì»¬ ?„œë²„ì—?„œ ?™•?¸?„ ?•´ë³´ì. "

categories:
  - Blog
tags:
  - [Blog, jekyll, Github, Git, baekjoon]

toc: true
toc_sticky: true
 
date: 2024-04-25
last_modified_at: 2024-05-06
---

2024-4-35?— ë°±ì?? 1927-ìµœì†Œ?™ ë¬¸ì œë¥? ????—ˆ?‹¤

https://www.acmicpc.net/problem/1927

![image](https://github.com/softkleenex/softkleenex.github.io/assets/92619941/e71e63ee-850f-45a9-a36f-99a5e5c58ea5)


ì²´ì¶œ?•œ ?†Œ?Š¤ì½”ë“œ?Š” ?‹¤?Œê³? ê°™ë‹¤.

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
    {}    //?™?´ ê½? ì°¼ë‹¤
    
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
//0 ?…? ¥?‹œ ë°°ì—´?˜ ìµœì†Œê°? ì¶œëŸ­, ê·? ë°°ì—´ ? œê±? 
// ??—°?ˆ˜ ?…? ¥?‹œ?— ë°°ì—´?— ê·? ê°? ?„£?Œ

    if(x == 0)
    {
        if(size == 0) //?¸?±?Š¤ê°? 0 >> ì¦?, ë°°ì—´?´ ?•„?˜ˆ ë¹„ì›Œ? ¸ ?ˆ?Š” ê²½ìš°
            printf("0\n");
        else//ë°°ì—´?— ë­ë¼?„ ?ˆ?Š” ê²½ìš°
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

ë¬¸ì œ?˜ ?‹œê°? ? œ?•œ?„ ?ƒê°í•˜ë©?, ?´?Š” ?ë£Œêµ¬ì¡°ì˜ ?™?„ ?´?š©?•˜?—¬ ????–´?•¼ ?•œ?‹¤. 
ì½”ë“œ ?„¤ëª…ì´ ì£¼ì„?œ¼ë¡? ?“¤?–´ê°? ì½”ë“œë¥? ì²¨ë???•œ?‹¤

```c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#define swap(a, b) do{int temp = a; a = b; b = temp;}while(0)

int heap[100000];
int size = 0;

//size >> ë°°ì—´?˜ ê°??š© ?¸?±?Š¤?´?‹¤. ë¹„ì›Œ? ¸?ˆ?„?–„?Š” 0, ê°’ì´ ?•˜?‚˜ ?ˆ?œ¼ë©? 1, ?‘˜ ?ˆ?œ¼ë©? 2......
//ë°°ì—´?˜ ìµœë?? ê¸¸ì´?Š” x?˜ ?´?•˜?´?‹¤.
//ë°°ì—´?˜ ?™œ?š© ?¸?±?Š¤?Š” 0?—?„œë¶??„°



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

//?¸?±?Š¤ 0ë¶??„° ?‹œ?‘?•˜?Š” ë°°ì—´-?™??? parent*2 + 1 > leftchild, parent*2+2 > right chlide,?´?‹¤. 
//(leftchild || right chlild)-1 /2 > parent?´?‹¤. 

void insert(int value)//?™?— ?ƒˆë¡œìš´ ê°’ì„ ?„£?„?–„?´?‹¤.
{
    if (size == 9999)
    {}    //?™?´ ê½? ì°¼ë‹¤
    
    //sizeê°? 9999(ì¦?, heap?˜ ?¬ê¸? -1)?´?¼?Š”ê²ƒì??, ?™?´ ê½? ì°¼ë‹¤?Š”ê²ƒì´?‹¤. ì¦?, ?…? ¥?„ ë°›ì?? ?•Šê³? ?„˜?–´ê°„ë‹¤.


    int index = size;
    heap[size] = value;
    size ++;

   //index?—?Š” insert?•˜ê¸? ? „?˜ size, size?—?Š” insert?•œ ?›„?˜ sizeê°? ?“¤?–´?ˆ?‹¤.
   //insertë¥? index?— ë¶?ë¶„ì— ?•˜????œ¼?‹ˆ - heap?˜ ê°??¥ ? ë¶?ë¶„ì— ?„£?—ˆ?œ¼?‹ˆ- index?—?„œë¶??„° ?œ„ë¡? ?˜¬?¼ê°?ë©´ì„œ ìµœì†Œ?™?„ ë§Œì¡±?•˜?Š”ì§? ê²??‚¬?•œ?‹¤.
   //indexë¥? ë³„ë„ë¡? ?„ ?–¸?•œ ?´?œ ?Š”, ê²??‚¬?‹¨ê³„ì—?„œ sizeë¥? ë²ˆí˜•?•´?•¼?•˜ë¯?ë¡?, indexë¥? ë³„ë„ë¡? ?„ ?–¸?•˜?—¬ index?— sizeë¥? ?„£?—ˆ?‹¤

    while ((index != 0) && (heap[parent(index)] > heap[index])) //ê²??‚¬ê°? ??‚˜ì§? ?•Š?•˜?œ¼ë©? -indexê°? rootê°? ?•„?‹ˆë©? - and 
										    //index??? index?˜ parentê°? ìµœì†Œ?™ ì¡°ê±´?— ë§ëŠ” ê²½ìš°?— ê²??‚¬?•œ?‹¤ 
    {
        swap(heap[index], heap[parent(index)]); //whileë¬¸ì„ ?†µê³¼í•œ ?ƒ?ƒœ?´ë¯?ë¡? index?˜ ê°’ê³¼ ê·? parent?˜ ê°’ì?? ë°”ë?Œì–´?•¼ ?•˜ê³?
        index = parent(index);//indexë¥? ê·? parentë¡? ë°”ê¾¸?–´?„œ ê²??‚¬ë¥? ê³„ì†?•œ?‹¤.
    }


}


//remove?›„?— ìµœì†Œ?™ ì¡°ê±´?„ ?œ ì§??•˜ê¸? ?œ„?•´ ?„ ?–¸?•œ ?•¨?ˆ˜ - removeë³´ë‹¤ ?œ„?— ?ˆ?–´?•¼?•œ?‹¤!

void minHeapify(int index)
{
    int left = leftChild(index);
    int right = rightChild(index);
    int smallest = index;

    if (left < size && heap[left] < heap[smallest])
        smallest = left;
    if(right < size && heap[right] < heap[smallest])
        smallest = right;


//right <size, left<sizeë¥? ?†µ?•´?„œ right??? leftê°? heap?˜ ë²”ìœ„?— ?“¤?–´??? ?ˆ?„?–„ë§? ?ƒê°í•œ?‹¤.

//?œ„?˜ ì¡°ê±´ë¬¸ë“¤?„ ?†µ?•´, index??? ê·? right, left?˜ ê°’ë“¤ì¤? smallest?•œê²ƒì´ smallest?— ?“¤?–´ê°? ?ˆ?‹¤.
    
    if (smallest != index)//indexê°? smallestê°? ?•„?‹Œê²½ìš° - ì¦?, ìµœì†Œ?™?„ ë§Œì¡±?‹œ?‚¤ì§? ?•Š?Š” ê²½ìš°?—
    { 
        swap(heap[index], heap[smallest]); //smallest???, index?˜ ê°’ì„ ?’¤ë°”ê¾¸ê³?,
        minHeapify(smallest);//?¬ê·?? ?œ¼ë¡? ?’¤ë°”ê¾¼ ê·? ê°’ì— ????•´ minHeapifyë¥? ?‹œ?–‰?•œ?‹¤. 
    }

}

//heap?˜ ìµœì†Œë¥? ? œê±°í•˜?Š” ?•¨?ˆ˜-ìµœì†Œ?™?´ë¯?ë¡?, ?™?˜ ê°??¥ ?œ„-ë°°ì—´?˜ ?¸?±?Š¤0?„ ? œê±°í•˜ê²Œëœ?‹¤.

int removeMin()
{
    if (size <= 0)
        return 0;
    //sizeê°? 0 ?´?•˜ > ?Œ?ˆ˜?Š” ?˜¤ë¥˜ì˜ ê²½ìš°?´ê³?, 0?¸ê²½ìš°?Š” ?™?— ?•„ë¬´ê²ƒ?„ ?—†?‹¤?Š”ê²ƒì´?‹¤    

    if (size == 1)
    {
        size -= 1;
        return heap[0];
    }

   //sizeê°? 1>heap?— ê°’ì´ ?•˜?‚˜ë§? ?ˆ?‹¤?Š”ê²?, heap[0]?´ ê·? ?œ ?¼?•œ ê°’ì´ë¯?ë¡? size -=1 ?„ ?•˜ê³? heap[0]?„ ë¦¬í„´?•œ?‹¤

    int root = heap[0];
    heap[0] = heap[size -1];
    size -= 1;
    minHeapify(0);
    return root;

//ê·? ?™¸?˜ ê²½ìš° > heap[0]?„ ë¦¬í„´?•˜ê³?, heap?˜ ê°??¥ ? ê°’ì„ heap[0]?œ¼ë¡? ê°?? ¸?˜¤ê³?, size -= 1?„ ?•˜ê³?, 0 ?—?„œë¶??„° minheapifyë¥? ?‹œ?–‰?•œ?‹¤.
 
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
//0 ?…? ¥?‹œ ë°°ì—´?˜ ìµœì†Œê°? ì¶œëŸ­, ê·? ë°°ì—´ ? œê±? 
// ??—°?ˆ˜ ?…? ¥?‹œ?— ë°°ì—´?— ê·? ê°? ?„£?Œ

    if(x == 0)
    {
        if(size == 0) //?¸?±?Š¤ê°? 0 >> ì¦?, ë°°ì—´?´ ?•„?˜ˆ ë¹„ì›Œ? ¸ ?ˆ?Š” ê²½ìš°
            printf("0\n");
        else//ë°°ì—´?— ë­ë¼?„ ?ˆ?Š” ê²½ìš°
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

?„?!!!!!! 