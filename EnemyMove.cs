using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class EnemyMove : MonoBehaviour
{
    Rigidbody2D rigid;
    public int NextMove;
    Animator anim;
    SpriteRenderer spriterederer;
    BoxCollider2D collider;

    void Awake()
    {
        rigid = GetComponent<Rigidbody2D>();
        anim = GetComponent<Animator>();
        spriterederer = GetComponent<SpriteRenderer>();
        collider = GetComponent<BoxCollider2D>();
        Think();
        Invoke("Think", 3); // 주어진 시간이 지난뒤, 지정된  함수를 실행하는 함수 Think 라는 함수를 넣고 , 5 라는 초단위를 넣음  
    }


    void FixedUpdate()
    {
        //   rigid.velocity = new Vector2(-1, rigid.velocity.y); // 단순히 왼쪽으로 이동 
        rigid.velocity = new Vector2(NextMove, rigid.velocity.y); // 랜덤 클래스를 넣었기때문에 nextmove 함수에 해당하는 -1 ~1 에 해당하는 방향으로감 단 한번만 선언했기때문에 한번만 랜덤의 방향으로 지정해서 감 
        // nextmove 에 3를 곱하니 속도가 증가 하고 nextmove 값은 안변하기 때문에 참고바람 

        //flatform check

        Vector2 frontVec = new Vector2(rigid.position.x + NextMove * 0.5f, rigid.position.y); // 현재위치에 + nextmove(랜덤값의 숫자 방향으로 한칸더보기위해  +해준것) 
        Debug.DrawRay(frontVec, Vector3.down, new Color(0, 1, 0));

        RaycastHit2D rayhit = Physics2D.Raycast(frontVec, Vector3.down, 1, LayerMask.GetMask("Flatform"));
        if (rayhit.collider == null)
        {
            if(spriterederer.flipY == true)
            {
                Invoke("DeActive", 1);
            }
          else turn();
            
           

            /* if (rayhit.distance < 0.5f)
             {
                 anim.SetBool("isJumping", false);
             }
             */
        }
    }
    void Think()
    {    //set next active
        NextMove = Random.Range(-1, 2);  //랜덤 수를 생성하는 로직 관련 클래스 > 중요사항 최소값은 포함되지만 최대값은 포함 안되기 때문에 -1~1 을 포함하려면 -1, 2 로 설정


       

        anim.SetInteger("WalkSpeed", NextMove); // bool 이 아닌 int 의 형태 integer 를 써야됨  sprite 애니메이션

        if (NextMove != 0)   // 방향 flip sprite 
            spriterederer.flipX = NextMove == 1;

        float nextthinktime = Random.Range(2f, 5f);
        Invoke("Think", nextthinktime); // recursive(재귀함수)

        // Think();  // 재귀함수 자기 함수안에 자기 함수를 호출함  하지만 속도가 엄청빠르게 돌아가기때문에 위험 
    }
    void turn()
        {
        NextMove *= -1;
        spriterederer.flipX = NextMove == 1;

        CancelInvoke();
        Invoke("Think", 3);
    }

    public void OnDamaged()
    {

        
        // sprite alpha
        spriterederer.color = new Color(1, 1, 1, 0.4f);
        // sprite filp y
        spriterederer.flipY = true;
        //colider  disable
        collider.enabled = false;
        // die effect jump
        rigid.AddForce(Vector2.up * 5, ForceMode2D.Impulse);
        // destroy
        
    }
  

    void DeActive()
    {
        gameObject.SetActive(false);
       
    }

    
}
