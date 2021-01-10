#include <string>
#include <fstream>
#include <vector>
#include <utility>
#include <stdexcept> 
#include <sstream>
#include <iostream>


struct osoba{
int ID;
char spol;
int dob;
std::string KrvnaGrupa;
char RHfaktor;
std::string HLA_A1;
std::string HLA_A2;
std::string HLA_B1;
std::string HLA_B2;
std::string HLA_DR1;
std::string HLA_DR2;
};


std::vector<std::pair<osoba,osoba>> read_csvD(std::string filename){  //ČITAMO DATA
    std::vector<std::pair<osoba, osoba>> result;
    std::pair<osoba,osoba> par;
    std::ifstream myFile(filename);
    if(!myFile.is_open()) throw std::runtime_error("Could not open file"); //PROVJERA JE LI SE UČITALA DATOTEKA
    std::string line, rijec;

    if(myFile.good()){
        std::getline(myFile, line);   //IZBACIMO PRVI RED JER SU IMENA STUPACA U CSV
    }
    osoba podaci;
    int brStupca = 0;
    std::size_t poz=0;
    while(std::getline(myFile, line)){ //ČITAMO RED PO RED
        std::stringstream ss(line);
        do{           //izvlačimo dio po dio DONORA
            rijec= line.substr(poz,line.find(',',poz)-poz);
            if(brStupca==0 || brStupca==11) podaci.ID=std::stoi(rijec);
            if(brStupca==1 || brStupca==12) podaci.spol=rijec.at(0);
            if(brStupca==2 || brStupca==13) podaci.dob=std::stoi(rijec);
            if(brStupca==3 || brStupca==14) podaci.KrvnaGrupa=rijec;
            if(brStupca==4 || brStupca==15) podaci.RHfaktor=rijec.at(0);
            if(brStupca==5 || brStupca==16) podaci.HLA_A1=rijec;
            if(brStupca==6 || brStupca==17) podaci.HLA_A2=rijec;
            if(brStupca==7 || brStupca==18) podaci.HLA_B1=rijec;
            if(brStupca==8 || brStupca==19) podaci.HLA_B2=rijec;
            if(brStupca==9 || brStupca==20) podaci.HLA_DR1=rijec;
            if(brStupca==10 || brStupca==21) podaci.HLA_DR2=rijec;
            poz=line.find(',',poz)+1;
            brStupca++;
            if(brStupca==11){   //Učitali smo Donora
            par.first=podaci;
            }
            if(brStupca==22){ //Učitali smo pacijenta
            par.second=podaci;
            }
        }while(line.find(',',poz)!=std::string::npos);
        rijec= line.substr(poz,line.find(',',poz)-poz);
        podaci.HLA_DR2=rijec;
        par.second=podaci;
        result.push_back(par); //UNOSIMO ZADNJI PAR JER WHILE PETLJA IZAĐE JEDNU RIJEČ RANIJE
        poz=0;
        brStupca = 0;
    }
    myFile.close();
    return result;
}

std::vector<osoba> read_csvA(std::string filename){  //ČITAMO ALTRUISTE
    std::vector<osoba> result;
    std::ifstream myFile(filename);
    if(!myFile.is_open()) throw std::runtime_error("Could not open file"); //PROVJERA JE LI SE UČITALA DATOTEKA
    std::string line, rijec;

    if(myFile.good()){
        std::getline(myFile, line);   //IZBACIMO PRVI RED
    }
    osoba podaci;
    int brStupca = 0;
    std::size_t poz=0;
    while(std::getline(myFile, line))  //ČITAMO RED PO RED
    {
        std::stringstream ss(line);
        do{            //izvlačimo dio po dio DONORA
            rijec= line.substr(poz,line.find(',',poz)-poz);          
            if(brStupca==0) podaci.ID=std::stoi(rijec);
            if(brStupca==1) podaci.spol=rijec.at(0);
            if(brStupca==2) podaci.dob=std::stoi(rijec);
            if(brStupca==3) podaci.KrvnaGrupa=rijec;
            if(brStupca==4) podaci.RHfaktor=rijec.at(0);
            if(brStupca==5) podaci.HLA_A1=rijec;
            if(brStupca==6) podaci.HLA_A2=rijec;
            if(brStupca==7) podaci.HLA_B1=rijec;
            if(brStupca==8) podaci.HLA_B2=rijec;
            if(brStupca==9) podaci.HLA_DR1=rijec;
            if(brStupca==10) podaci.HLA_DR2=rijec;
            poz=line.find(',',poz)+1;
            brStupca++;
        }while(line.find(',',poz)!=std::string::npos);
        rijec= line.substr(poz,line.find(',',poz)-poz);
        podaci.HLA_DR2=rijec;
        result.push_back(podaci); //ANALOGNO DATA SAMO DODAJEMO OSOBU, A NE PAR I ISTO IZAĐE JEDAN RANIJE ZBOG SPECIFIKACIJA
        brStupca=0;
        poz=0;
    }
    myFile.close();
    return result;
}

inline int match(std::string donor_HLA, std::string pacijent_HLA1, std::string pacijent_HLA2) //SVI EKVIVALENTI KOJE SAM NAŠAO DA IH IMAMO SU POPISANI
{
    if(donor_HLA==pacijent_HLA1 || donor_HLA==pacijent_HLA2) return 1;
    if(donor_HLA=="A2" && (pacijent_HLA1=="A203" || pacijent_HLA2=="A203" || pacijent_HLA1=="A210" || pacijent_HLA2=="A210")) return 1;
    if(donor_HLA=="B5" && (pacijent_HLA1=="B78" || pacijent_HLA2=="B78")) return 1;
    if(donor_HLA=="B7" && (pacijent_HLA1=="B703" || pacijent_HLA2=="B703" || pacijent_HLA1=="B2708" || pacijent_HLA2=="B2708")) return 1;
    if(donor_HLA=="DR3" && (pacijent_HLA1=="DR17" || pacijent_HLA2=="DR17" || pacijent_HLA1=="DR18" || pacijent_HLA2=="DR18")) return 1;
    if(donor_HLA=="DR2" && (pacijent_HLA1=="DR15" || pacijent_HLA2=="DR15" || pacijent_HLA1=="DR16" || pacijent_HLA2=="DR16")) return 1;
    if(donor_HLA=="DR5" && (pacijent_HLA1=="DR11" || pacijent_HLA2=="DR11" || pacijent_HLA1=="DR12" || pacijent_HLA2=="DR12")) return 1;
    if(donor_HLA=="DR6" && (pacijent_HLA1=="DR13" || pacijent_HLA2=="DR13" || pacijent_HLA1=="DR14" || pacijent_HLA2=="DR14")) return 1;  
    return 0;
}

int kompatibilnost(osoba donor, osoba pacijent)
{
    int komp=100; //KREĆEMO OD 100%, A ODUZIMAMO VRIJEDNOSTI KOJE SAM UNAPRIJED IZRAČUNAO KAO 50*2/6=17
                 // KOEFICIJENTI SU PODLOŽNI PROMJENAMA PO VOLJI, JA SAM OTPRILIKE STAVIO, VJEROJATNO NIJE NAJBOLJE
    //PACIJENTI NISU KOMPATIBLINE KRVNE GRUPE
    if(pacijent.KrvnaGrupa=="0" && donor.KrvnaGrupa!="0") return 0;
    if(pacijent.KrvnaGrupa=="A" && (donor.KrvnaGrupa=="B" || donor.KrvnaGrupa=="AB")) return 0;
    if(pacijent.KrvnaGrupa=="B" && (donor.KrvnaGrupa=="A" || donor.KrvnaGrupa=="AB")) return 0;
    //RAČUNAMO NA KOLIKO MJESTA SE HLA PODUDARA
    int HLA_jednaki=0;
    HLA_jednaki=HLA_jednaki+match(donor.HLA_A1, pacijent.HLA_A1,pacijent.HLA_A2);
    HLA_jednaki=HLA_jednaki+match(donor.HLA_A2, pacijent.HLA_A1,pacijent.HLA_A2);
    HLA_jednaki=HLA_jednaki+match(donor.HLA_B1, pacijent.HLA_B1,pacijent.HLA_B2);
    HLA_jednaki=HLA_jednaki+match(donor.HLA_B2, pacijent.HLA_B1,pacijent.HLA_B2);
    HLA_jednaki=HLA_jednaki+match(donor.HLA_DR1, pacijent.HLA_DR1,pacijent.HLA_DR2);
    HLA_jednaki=HLA_jednaki+match(donor.HLA_DR2, pacijent.HLA_DR1,pacijent.HLA_DR2);

    //HLA MORA SE PODUDARATI NA NAJMANJE 4, A IDEALNO 6 MJESTA
    if(HLA_jednaki<4) return 0;
    if(HLA_jednaki==4) komp=komp-17;
    if(HLA_jednaki==5) komp=komp-34;
    //PACIJENT NISU JEDNAKE KRVNE GRUPE, ALI TRANSPLANTACIJE JE MOGUĆA
    if((pacijent.KrvnaGrupa=="A" || pacijent.KrvnaGrupa=="B" || pacijent.KrvnaGrupa=="AB") && donor.KrvnaGrupa=="0") komp=komp-6;
    if(pacijent.KrvnaGrupa=="AB" && (donor.KrvnaGrupa=="A" || donor.KrvnaGrupa=="B")) komp=komp-6;
    //RAZIČITI RH FAKTOR DAJE MALO MANJE ŠANSE ZA USPJEH
    if(pacijent.RHfaktor=='+' && donor.RHfaktor=='-') komp=komp-2;
    if(pacijent.RHfaktor=='-' && donor.RHfaktor=='+') komp=komp-4;
    //JEDNAKA DOBNA SKUPINA DAJE BOLJU MOGUĆNOST PRIHVAĆANJA ORGANA   // OVDJE LAKO MAKNEMO AKO SAM NEŠTA KRIVO
    if(pacijent.dob<15 && donor.dob>65) komp=komp-10;
    if(pacijent.dob<15 && donor.dob<65 && donor.dob>15) komp=komp-5;
    if(pacijent.dob>15 && pacijent.dob<65 && donor.dob>65) komp=komp-10;
    if(pacijent.dob>15 && pacijent.dob<65 && donor.dob<15) komp=komp-10;
    if(pacijent.dob>65 && donor.dob<15) komp=komp-2;
    if(pacijent.dob>65 && donor.dob<65 && donor.dob>15) komp=komp-5;

    if(komp<0) komp=0;
    return komp;
}

int** IzracunajMatricu(std::vector<std::pair<osoba,osoba>> Data, int N) //SAMO DATA BEZ ALTURISTA
{
    int**Matrix;
    int i,j;
    Matrix= new int*[N];
    for(i=0; i<N; ++i)
        Matrix[i]=new int[N];
    for(i=0; i<N; ++i)
        for(j=0; j<N; ++j)
            {
                Matrix[i][j]=kompatibilnost(Data.at(i).first, Data.at(j).second);
            }
    return Matrix;
}

int** IzracunajMatricu(std::vector<std::pair<osoba,osoba>> Data, std::vector<osoba> Alt, int N) //DATA I ALTRUISTI
{
    int** Matrix;
    int i,j;
    int M=Alt.size();
    Matrix= new int*[N];
    for(i=0; i<N; ++i)
        Matrix[i]=new int[N];

    for(i=0; i<N; ++i)  ///NITKO NEĆE DONIRATI ALTURISTIMA PA JE AUTOMATSKI 0
        for(j=0; j<M; ++j){
            Matrix[i][j]=0;
        }

    for(i=0; i<M; ++i) //DIO U KOJEM ALTURISTI DONIRAJU
        for(j=M; j<N; ++j){
            Matrix[i][j]=kompatibilnost(Alt.at(i), Data.at(j-M).second); // j-M JER DATA IDE OD 0-"BROJ DATA", A j OD 0-"BROJ LJUDI(ALTRUISTI+DATA)"
            }

    for(i=M; i<N; ++i)
        for(j=M; j<N; ++j){
                Matrix[i][j]=kompatibilnost(Data.at(i-M).first, Data.at(j-M).second); //ANALOGNO i-M i KAO IZNAD
            }

    return Matrix;
}


int main(int argc, char **argv) { //PRVI ARGUMENT JE UVIJEK IME FUNKCIJE PA JE argc=1+KOLIKO IMENA DATOTEKA DAMO
                                  //PRVO UNOSIMO IME DATA DATOTEKE PA ONDA ALTRUISTA ILI SAMO DATA DATOTEKE (OBAVEZNO .csv STAVITI)
    std::string dataset, altruisti;
    std::vector<std::pair<osoba,osoba>> Data;
    std::vector<osoba> Alt;
    int** Matrix;
    int velicina;
    std::string Ime;
    switch (argc)
    {
    case 2: //UČITALI SMO SAMO DATA SET ZA CIKLUSE
        dataset=argv[1];
        Data = read_csvD(dataset);
        velicina=Data.size();
        if(velicina>0) {
            Matrix=IzracunajMatricu(Data, velicina);
        }
        Ime.append("Matrica_");
        Ime.append(std::to_string(Data.size()));
        break;

    case 3: //UČITALI SMO DATASET ZA ALTURISTE
        dataset=argv[1];
        altruisti=argv[2];
        Data = read_csvD(dataset);
        Alt=read_csvA(altruisti);
        velicina=Data.size()+Alt.size();
        if(velicina>0) {
            Matrix=IzracunajMatricu(Data, Alt, velicina);
        }
        Ime.append("Matrica_");
        Ime.append(std::to_string(Data.size()));
        Ime.append("X");
        Ime.append(std::to_string(Alt.size()));
        break;

    default: //NISMO UČITALI IMENA DATOTEKA
        break;
    }
    int k,l;

    std::ofstream output(Ime); //ZAPISUJEMO MATRICU U DATOTEKU  
    for (k=1; k<velicina; k++)
    {
        for (l=1; l<velicina; l++)
        {
            output << Matrix[k][l] << ",";
        }
        output << std::endl;
    }
    // IME DATOTEKE KOJA SE STVORI JE "Matrica_'veličina data'" ILI "Matrica_'veličina data'X'velicina altruista'"
    return 0;
}