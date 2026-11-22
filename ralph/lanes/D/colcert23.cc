#include <algorithm>
#include <array>
#include <iostream>
#include <vector>
using namespace std;
struct Search {
    int population, budget; array<int,6> demand; int matrix[6][6]{};
    void visit(vector<int> deck,int col,int spent){
        if(col==6){for(int mask:deck)cout<<mask<<' ';cout<<'\n';return;}
        int used[6]{}; vector<int> picks;
        auto choose=[&](auto&& self,int start)->void {
            if((int)picks.size()==demand[col]){
                int debit=spent;
                for(int peer=0;peer<col;peer++){
                    int known=matrix[col][peer],count=used[peer]; if(known<0){if(count)return;continue;}
                    int total=known+count;if(total<1||total>3)return;
                    if(total==1&&++debit>budget)return;
                }
                vector<int> next=deck;for(int slot:picks)next[slot]|=1<<col;sort(next.begin(),next.end());visit(next,col+1,debit);return;
            }
            for(int slot=start;slot<=population-(demand[col]-(int)picks.size());slot++){
                int mask=deck[slot];if(slot>start&&mask==deck[slot-1])continue;
                bool ok=true;for(int peer=0;peer<col;peer++)if(mask>>peer&1){if(matrix[col][peer]<0||matrix[col][peer]+used[peer]>=3)ok=false;}
                if(!ok)continue;for(int peer=0;peer<col;peer++)used[peer]+=(mask>>peer)&1;
                picks.push_back(slot);self(self,slot+1);picks.pop_back();for(int peer=0;peer<col;peer++)used[peer]-=(mask>>peer)&1;
            }
        };choose(choose,0);
    }
};
int main(){Search search;if(!(cin>>search.population>>search.budget))return 2;for(int &value:search.demand)cin>>value;for(int row=0;row<6;row++)for(int col=0;col<row;col++)cin>>search.matrix[row][col];if(!cin)return 3;search.visit(vector<int>(search.population),0,0);}
