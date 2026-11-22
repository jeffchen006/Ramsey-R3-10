#include <fstream>
#include <unordered_map>

template<int Width> struct PathDeck {
    using Core=std::array<int,Width>;
    using Slots=std::array<Mask,Width>;
    std::array<std::unordered_map<Mask,std::vector<unsigned>>,1<<Width> ids;
    std::vector<Slots> patterns;
    void load(const std::string& filename){
        std::ifstream input(filename);assert(input);std::string line;
        while(std::getline(input,line)){
            std::istringstream fields(line);std::string field;std::vector<int> exterior;
            while(fields>>field){auto pos=field.find(':');int mask=std::stoi(field.substr(0,pos)),size=std::stoi(field.substr(pos+1));assert(mask>=0&&mask<(1<<Width));while(size--)exterior.push_back(mask);}
            assert(int(exterior.size())==order-Width);
            for(int direction=0;direction<2;++direction){
                unsigned id=patterns.size();Slots pattern{};
                for(unsigned slot=0;slot<exterior.size();++slot){Mask mask=exterior[slot];while(mask)pattern[take(mask)]|=bit(slot);}patterns.push_back(pattern);
                for(int keep=0;keep<(1<<Width);++keep)if(count(keep)>=4){Mask hash=0;for(int mask:exterior)hash+=HubDeck::mix(mask&keep);ids[keep][hash].push_back(id);}
                for(int& mask:exterior){int flipped=0;for(int pos=0;pos<Width;++pos)if(mask&(1<<pos))flipped|=1<<(pos<2?(pos^(1-Width%2)):Width+1-pos);mask=flipped;}
            }
        }
    }
    bool matches(const Core& core,const Slots& pattern,Mask others,const Rows& lo,const Rows& hi) const {
        std::array<Mask,40> options{};int rows=0;
        while(others){int point=take(others);Mask sites=bit(order-Width)-1;for(int pos=0;pos<Width;++pos){if(lo[point]&bit(core[pos]))sites&=pattern[pos];if(!(hi[point]&bit(core[pos])))sites&=~pattern[pos];}if(!sites)return false;options[rows++]=sites;}
        std::sort(options.begin(),options.begin()+rows,[](Mask left,Mask right){return count(left)<count(right);});
        std::array<int,40> owner{};owner.fill(-1);
        for(int row=0;row<rows;++row){Mask seen=0;auto place=[&](auto&& self,int point)->bool{Mask sites=options[point];while(sites&~seen){sites&=~seen;int site=take(sites);seen|=bit(site);if(owner[site]<0||self(self,owner[site])){owner[site]=point;return true;}}return false;};if(!place(place,row))return false;}
        return true;
    }
    bool fits(const Rows& lo,const Rows& hi,Rows* forced=nullptr,Rows* allowed=nullptr)const{
        Mask fixed=0;for(int idx=0;idx<order;++idx)if(count(lo[idx])==degree)fixed|=bit(idx);
        for(int first=0;first<order;++first){Mask neighbors=lo[first];while(neighbors){
            int second=take(neighbors);Core core{first,second};Mask block=(lo[first]|lo[second])&~(bit(first)|bit(second));
            auto visit=[&](auto&& self,int length,Mask used)->bool{
                if(length==Width){
                    if(core[2]>core[Width-1]||(!(Width%2)&&(hi[core[2]]&bit(core[Width-1]))))return true;
                    if(count(used&fixed)<4)return true;
                    int keep=0;std::array<int,40> labels{};
                    for(int pos=0;pos<Width;++pos)if(fixed&bit(core[pos])){keep|=1<<pos;Mask sites=lo[core[pos]];while(sites)labels[take(sites)]|=1<<pos;}
                    Mask sites=all^used,hash=0;while(sites)hash+=HubDeck::mix(labels[take(sites)]);
                    auto it=ids[keep].find(hash);if(it==ids[keep].end())return false;
                    if(keep+1==(1<<Width)||it->second.size()>32)return true;
                    if(!forced||it->second.size()>12){for(unsigned id:it->second)if(matches(core,patterns[id],all^used,lo,hi))return true;return false;}
                    std::array<int,40> ones{},zeros{};bool found=false;
                    for(unsigned id:it->second){const Slots& pattern=patterns[id];if(!matches(core,pattern,all^used,lo,hi))continue;
                        found=true;Mask outside=all^used;while(outside){int point=take(outside);Mask options=bit(order-Width)-1;
                            for(int pos=0;pos<Width;++pos){if(lo[point]&bit(core[pos]))options&=pattern[pos];if(!(hi[point]&bit(core[pos])))options&=~pattern[pos];}
                            assert(options);for(int pos=0;pos<Width;++pos){if(options&pattern[pos])ones[point]|=1<<pos;if(options&~pattern[pos])zeros[point]|=1<<pos;}
                        }
                    }
                    if(!found)return false;
                    Mask outside=all^used;while(outside){int point=take(outside);for(int pos=0;pos<Width;++pos){if(!(ones[point]&(1<<pos)))cut(*allowed,point,core[pos]);if(!(zeros[point]&(1<<pos)))join(*forced,point,core[pos]);}}
                    return true;
                }
                Mask sites=(length==2?lo[first]:lo[core[length-1]])&block&~used;while(sites){int point=take(sites);core[length]=point;if(!self(self,length+1,used|bit(point)))return false;}return true;
            };
            if(!visit(visit,2,bit(first)|bit(second)))return false;
        }}return true;
    }
    bool missing(const Rows& lo,const Rows& hi,Rows& allowed)const{
        Mask fixed=0;for(int idx=0;idx<order;++idx)if(count(lo[idx])==degree)fixed|=bit(idx);
        for(int first=0;first<order;++first){Mask neighbors=hi[first];while(neighbors){
            int second=take(neighbors);bool root_unknown=!(lo[first]&bit(second));Core core{first,second};Mask block=(lo[first]|lo[second])&~(bit(first)|bit(second));
            if(count(block)<Width-2||count((block|bit(first)|bit(second))&fixed)<5)continue;
            auto visit=[&](auto&& self,int length,Mask used,int before,int after)->void{
                if(length==Width){
                    if(before<0||core[2]>core[Width-1]||(!(Width%2)&&(hi[core[2]]&bit(core[Width-1]))))return;
                    if(count(used&fixed)<5||!(allowed[before]&bit(after)))return;
                    int keep=0;std::array<int,40> labels{};for(int pos=0;pos<Width;++pos)if(fixed&bit(core[pos])){keep|=1<<pos;Mask sites=lo[core[pos]];while(sites)labels[take(sites)]|=1<<pos;}
                    Mask sites=all^used,hash=0;while(sites)hash+=HubDeck::mix(labels[take(sites)]);
                    auto it=ids[keep].find(hash);if(it!=ids[keep].end()){
                        if(it->second.size()>4||keep+1==(1<<Width))return;
                        for(unsigned id:it->second)if(matches(core,patterns[id],all^used,lo,hi))return;
                    }
                    cut(allowed,before,after);return;
                }
                int previous=length==2?first:core[length-1];Mask sites=lo[previous]&block&~used;
                while(sites){int point=take(sites);core[length]=point;self(self,length+1,used|bit(point),before,after);}
                if(before<0&&length>2){sites=(allowed[previous]&~lo[previous])&block&~used&lo[(length%2)?second:first];while(sites){int point=take(sites);core[length]=point;self(self,length+1,used|bit(point),previous,point);}}
            };
            visit(visit,2,bit(first)|bit(second),root_unknown?first:-1,root_unknown?second:-1);
        }}return allowed!=hi;
    }
};
