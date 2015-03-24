
#include<iostream>
#include<cstdlib>
#include<list>
#include<utility>
#include<map>
#include<vector>
#include<cassert>
#include<cmath>



using namespace std;

typedef unsigned char Symbol;
typedef vector<Symbol> Sequence;
typedef list<Sequence> Sequences;

size_t radius;
size_t alphaSize;
size_t further;

Sequence sequence;
Symbol nextSymbol;
Sequences bestSequences;
size_t bestLimit;

class MatchArray {
	public:
		inline void resize(){
			data.resize((alphaSize-2)*(alphaSize-1)/2+alphaSize-1,0);
		}
		inline size_t missing(){
			size_t count=0;
			for(vector<size_t>::iterator i=data.begin();i!=data.end();++i){
				if(*i==0)++count;
			}
			return count;
		}
		inline bool done(){
			for(vector<size_t>::iterator i=data.begin();i!=data.end();++i){
				if(*i==0)return false;
			}
			return true;
		}
		template<class iter>
		inline void update(Symbol a, iter b, iter e, int adj){
			for(;b!=e;++b){
				assert(a<alphaSize);
				assert(*b<alphaSize);
				if(a!=*b)
					data[(a>*b)?(a*(a-1)/2+(*b)):((*b)*((*b)-1)/2+a)]+=adj;
			}
		}
	private:
		vector<size_t> data;
}matches;

inline void push(Symbol n){
	if(sequence.size()<radius) matches.update(n,sequence.begin(),sequence.end(),1);
	else matches.update(n,sequence.rbegin(),sequence.rbegin()+radius,1);
	sequence.push_back(n);
}

inline void pop(){
	assert(sequence.size()>0);
	Symbol n=sequence.back();
	sequence.pop_back();
	if(sequence.size()<radius) matches.update(n,sequence.begin(),sequence.end(),-1);
	else matches.update(n,sequence.rbegin(),sequence.rbegin()+radius,-1);
}

bool search(){
	assert(further==0 || !matches.done());
	assert(nextSymbol<=alphaSize);
	assert(bestSequences.size()<=bestLimit);
	if(further==0){
		if(matches.done()){
			bestSequences.push_back(sequence);
			return true;
		}else return !bestSequences.empty();
	}
	if(matches.missing()>further*radius)return false;
	--further;
	if(sequence.size()>1){
		for(	Symbol i=0,j=sequence.back();
				(i<j) && (bestSequences.size()<bestLimit);
				++i){
			push(i);
			search();
			pop();
		}
		for(
				Symbol i=sequence.back()+1;
				(i<nextSymbol) && (bestSequences.size()<bestLimit);
				++i){
			push(i);
			search();
			pop();
		}
	}
	if((nextSymbol<alphaSize) && (bestSequences.size()<bestLimit)){
		push(nextSymbol++);
		search();
		pop();
		--nextSymbol;
	}
	++further;
	return !bestSequences.empty();
}

size_t lowerBound(){
	int working=int(ceil((alphaSize-1)/double(2*radius)));
	working*=alphaSize;
	for(size_t i=1;i<=radius+1;++i){
		working+=int(ceil((alphaSize+radius-i)/double(radius*2)));
		working-=int(ceil((alphaSize-1)/double(radius*2)));
	}
	return working;
}

int main(int argc, char** argv){
	if(argc<3||argc>4){
		cerr << "Usage: " << argv[0] << " size_of_alphabet radius [how_many=1]" << endl;
		return 1;
	}
	alphaSize=atoi(argv[1]);
	radius=atoi(argv[2]);
	bestLimit=(argc==4)?(atoi(argv[3])):1;

	matches.resize();

	for(further=lowerBound();!search();++further);

	cout << "Length: " << bestSequences.front().size() << endl;
	cout << "Length Lower Bound: " << lowerBound() << endl;
	cout << "Sequences: " << bestSequences.size() << endl;
	for(Sequences::iterator i=bestSequences.begin();i!=bestSequences.end();++i){
		cout << "Sequence: ";
		for(Sequence::iterator j=i->begin();j!=i->end();++j) cout << int(*j);
		cout << endl;
	}

}

