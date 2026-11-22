#include <fstream>
#include <unordered_map>
#include <unordered_set>

struct HubDeck {
    std::array<std::unordered_set<Mask>,256> buckets;
    struct Pattern{std::array<Mask,8> coordinate{};Mask anchor_mark=0,marked_slots=0;};
    std::vector<Pattern> patterns;
    std::array<std::unordered_map<Mask,std::vector<unsigned>>,256> ids;
    static Mask mix(Mask val){val+=0x9e3779b97f4a7c15ULL;val=(val^(val>>30))*0xbf58476d1ce4e5b9ULL;val=(val^(val>>27))*0x94d049bb133111ebULL;return val^(val>>31);}
    void load(const std::string& file){
        std::ifstream input(file);assert(input);std::string line;
        while(std::getline(input,line)){
            std::istringstream fields(line);Mask mark=0;std::vector<int> sites;
            std::vector<int> exterior;std::string term;while(fields>>term){auto sep=term.find(':');int size=std::stoi(term.substr(sep+1));while(size--)exterior.push_back(std::stoi(term.substr(0,sep)));}
            assert(int(exterior.size())==order-8);
            for(int direction=0;direction<2;++direction){
                unsigned current=patterns.size();
                if(mode&256){Pattern pattern;for(int site:sites){if(site<8)pattern.anchor_mark|=bit(site);else pattern.marked_slots|=bit(site-8);}for(unsigned slot=0;slot<exterior.size();++slot)for(int pos=0;pos<8;++pos)if(exterior[slot]&(1<<pos))pattern.coordinate[pos]|=bit(slot);patterns.push_back(pattern);}
                for(int keep=0;keep<256;++keep){
                    if(count(keep)<4)continue;
                    Mask hash=0;for(int site:sites)hash+=mix(512+(site<8?256+site:(exterior[site-8]&keep)));
                    for(int mask:exterior)hash+=mix(mask&keep);
                    buckets[keep].insert(hash);
                    if(mode&256)ids[keep][hash].push_back(current);
                }
                for(int& site:sites)if(site<8)site=site<2?1-site:9-site;
                for(int& mask:exterior){int next=0;for(int idx=0;idx<8;++idx)if(mask&(1<<idx))next|=1<<(idx<2?1-idx:9-idx);mask=next;}
            }
        }
    }
    bool mapped(const Pattern& pattern,const std::array<int,8>& core,const Rows& lo,const Rows& hi,Mask outside,Mask hub)const {
        Mask anchor_mark=0;for(int pos=0;pos<8;++pos)if(hub&bit(core[pos]))anchor_mark|=bit(pos);
        if(anchor_mark!=pattern.anchor_mark)return false;
        std::array<Mask,40> allowed{};int rows=0;
        while(outside){int point=take(outside);Mask sites=bit(order-8)-1;sites&=(hub&bit(point))?pattern.marked_slots:~pattern.marked_slots;
            for(int pos=0;pos<8;++pos){if(lo[point]&bit(core[pos]))sites&=pattern.coordinate[pos];if(!(hi[point]&bit(core[pos])))sites&=~pattern.coordinate[pos];}
            if(!sites)return false;
            allowed[rows++]=sites;
        }
        std::sort(allowed.begin(),allowed.begin()+rows,[](Mask left,Mask right){return count(left)<count(right);});
        std::array<int,40> mate{};mate.fill(-1);
        for(int row=0;row<rows;++row){Mask seen=0;auto place=[&](auto&& self,int point)->bool{Mask options=allowed[point];while(options&~seen){options&=~seen;int slot=take(options);seen|=bit(slot);if(mate[slot]<0||self(self,mate[slot])){mate[slot]=point;return true;}}return false;};if(!place(place,row))return false;}
        return true;
    }
    bool fits(const Rows& lo,const Rows& hi,Mask hub)const {
        for(int first=0;first<order;++first){
            Mask edges=lo[first];while(edges){
                int second=take(edges);std::array<int,8> core{first,second};Mask block=(lo[first]|lo[second])&~(bit(first)|bit(second));
                auto walk=[&](auto&& self,int length,Mask used)->bool{
                    if(length==8){
                        if(core[2]>core[7] || (hi[core[2]]&bit(core[7])))return true;
                        int keep=0;for(int pos=0;pos<8;++pos)if(count(lo[core[pos]])==degree)keep|=1<<pos;
                        if(count(keep)<4)return true;
                        std::array<int,40> masks{};for(int pos=0;pos<8;++pos)if(keep&(1<<pos)){Mask neighbors=lo[core[pos]];while(neighbors)masks[take(neighbors)]|=1<<pos;}
                        Mask rest=all^used,hash=0,sites=hub;while(sites){int site=take(sites),code=masks[site];for(int pos=0;pos<8;++pos)if(core[pos]==site)code=256+pos;hash+=mix(512+code);}while(rest)hash+=mix(masks[take(rest)]);
                        if(!buckets[keep].count(hash))return false;
                        if((mode&256)&&keep!=255){const auto& choices=ids[keep].at(hash);if(choices.size()<=64){for(auto id:choices)if(mapped(patterns[id],core,lo,hi,all^used,hub))return true;return false;}}
                        return true;
                    }
                    Mask choices=(length==2?lo[first]:lo[core[length-1]])&block&~used;
                    while(choices){int point=take(choices);core[length]=point;if(!self(self,length+1,used|bit(point)))return false;}
                    return true;
                };
                if(!walk(walk,2,bit(first)|bit(second)))return false;
            }
        }
        return true;
    }
};
