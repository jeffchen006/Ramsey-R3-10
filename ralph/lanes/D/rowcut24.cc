#include <bit>
#include <iostream>
#include <vector>
using namespace std;
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);string key;int outer,points,need,loss;while(cin>>key>>outer>>points>>need>>loss){vector<unsigned> cols(points);vector<int> known(points);for(auto &value:cols)cin>>value;for(auto &value:known)cin>>value;int count=0;unsigned witness=0;for(unsigned mask=(1u<<need)-1; mask<(1u<<outer);){int used=loss;bool ok=true;for(int pos=0;pos<points&&ok;pos++){int common=popcount(mask&cols[pos]);if(known[pos]<0)ok=!common;else{int total=common+known[pos];ok=total<=3;used+=max(0,2-total);ok&=used<=1;}}if(ok){count=1;witness=mask;break;}if(!mask)break;unsigned low=mask&-mask,next=mask+low;mask=next+(((next^mask)/low)>>2);}cout<<key<<'\t'<<count<<'\t'<<witness<<'\n';}}
