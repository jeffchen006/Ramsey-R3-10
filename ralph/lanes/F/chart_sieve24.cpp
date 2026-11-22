#define main original_six_main
#include "six_complete.cpp"
#undef main
int main(int argc,char** argv){
    assert(argc==5);const int width=2048,blocks=width/64;const int limit=stoi(argv[1]),left=stoi(argv[2]),right=stoi(argv[3]);assert(left>=0&&left<right&&right<=(1<<19));
    vector<pair<int,int>> pairs;vector<Word> columns;ifstream matrix("columns.tsv");int source,dest;Word form;
    while(matrix>>source>>dest>>form){pairs.emplace_back(source,dest);columns.push_back(form);}assert(pairs.size()==49);
    vector<Table> bank;ifstream input("bank.tsv");string line;while(int(bank.size())<limit&&getline(input,line)){istringstream entry(line);Word support;int rank;entry>>support>>rank;Table table;while(entry>>form)table.rows.push_back(form);assert(int(table.rows.size())==rank&&rank<=8);
        table.lookup.resize((1<<rank)*blocks);for(int key=0;key<width;++key)table.lookup[syndrome(key,table.rows)*blocks+key/64]|=bit(key%64);bank.push_back(move(table));}assert(int(bank.size())==limit);
    ofstream counts(argv[4]);assert(counts);int visited=0,strict=0;
    for(int prefix=left;prefix<right;++prefix){Word high=Word(prefix)*width;array<Word,blocks> alive;alive.fill(~Word(0));for(const auto& table:bank){const Word* lookup=table.lookup.data()+syndrome(high,table.rows)*blocks;for(int block=0;block<blocks;++block)alive[block]&=~lookup[block];}
        for(int block=0;block<blocks;++block)for(Word rest=alive[block];rest;rest&=rest-1){Word key=high+64*block+low(rest);Graph graph{};for(int vertex=0;vertex<32;++vertex)graph[vertex]=bit(vertex^1);for(int index=0;index<49;++index){auto [left_site,right_site]=pairs[index];int flip=1^__builtin_parityll(columns[index]&key);for(int side:{0,1})edge(graph,2*left_site+side,2*right_site+(side^flip));}
            ++visited;if(independent(graph,bit(32)-1,10))continue;++strict;cout<<key<<'\n';}
    }counts<<left<<' '<<right<<' '<<Word(right-left)*width<<' '<<visited<<' '<<strict<<'\n';
}
