#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cassert>
#include <math.h>

const int TAB_SIZE = 1000;

using namespace std;

class Plot {
		public:
				Plot()
				{
						x.reserve(TAB_SIZE);
						y.reserve(TAB_SIZE);
						parmname = "";
				}

				friend istream& operator>>(istream& s, Plot& p);

				bool operator< (const Plot& other) const ;

				bool IsInited() {
						return (x.size() > 0);
				}

				const string& name() const {
						return parmname;
				}

				bool differs( const Plot* other, double epsilon ) const;

				bool empty() const {
					return ( y.size() == 0 );
				}

		private:
			string parmname;
			vector<double> x;
			vector<double> y;
};

bool Plot::differs( const Plot* other, double epsilon ) const
{
	vector< double >::const_iterator i;
	vector< double >::const_iterator j = other->y.begin();

	for ( i = y.begin(); i != y.end(); i++ )
		if ( fabs( *i - *j++ ) > epsilon )
			return 1;
	return 0;
}

istream& operator>>(istream& s, Plot& p)
{
	string n = "";
	double x, y;

	while((n != "/plotname") && (s >> n))
			;

	s >> n;
	p.parmname = n;

	while (s >> y) {
			p.y.push_back(y);
	}
	// s.clear();
	// s.clear(ios_base::badbit); // clear error state
	if (!s.eof() || p.y.size() > 0 )
			s.clear();
	cerr << ".";
	return s;
}

Plot* findPlot( vector< Plot* >& p, const string& name )
{
	vector< Plot* >::iterator i;
	for ( i = p.begin(); i != p.end(); i++ )
		if ( (*i)->name() == name )
			return *i;
	return 0;
}

int main(int argc, char** argv)
{
		if (argc < 4) {
				cerr << "Usage: " << argv[0] << " file1 file2 epsilon\n";
				return 0;
		}
		fstream f0( argv[1] );
		fstream f1( argv[2] );
		double EPSILON = atof( argv[3] );
		assert( f0.good() );
		assert( f1.good() );
		assert( EPSILON > 0.0 );

		vector< Plot* > p0;
		vector< Plot* > p1;
		Plot* p;

		for ( p = new Plot(); f0 >> *p; p = new Plot )
			p0.push_back( p );

		for ( p = new Plot(); f1 >> *p; p = new Plot )
			p1.push_back( p );
		
		if ( p0.size() != p1.size() ) {
			cout << argv[1] << ": diff # of plots\n";
			return 0;
		}

		if ( p0.size() == 0 ) {
			cout << argv[1] << ": empty plots\n";
			return 0;
		}
		
		if ( p0[0]->empty() || p1[0]->empty() ) {
			cout << argv[1] << ": empty plots\n";
			return 0;
		}
	
		// Go through all plots in p0 and compare with matching plots in p1
		// If any point differs by more than EPSILON, complain.
		vector< Plot* >::iterator i;
		for ( i = p0.begin(); i != p0.end(); i++ ) {
			Plot* temp = findPlot( p1, ( *i )->name() );
			if ( !temp ) {
				cout << argv[1] << ": " << ( *i )->name() << 
					": no matching plotname\n";
				return 0;
			}
			if ( ( *i )->differs( temp, EPSILON ) ) {
				cout << argv[1] << ": " << ( *i )->name() << 
					": plot differs\n";
				return 0;
			}
		}
		cout << ".";
}
