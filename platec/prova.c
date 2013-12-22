#include <stdio.h>
#include <stddef.h>
#include "lithosphere.hpp"
#include "platecapi.hpp"

int main(int argc, char* argv[])
{
    size_t id = platec_api_create(512,0.65f,60,0.02f,1000000, 0.33f, 2, 10);       
    printf("Created %i\n",id);
    lithosphere* l = platec_api_get_lithosphere(0);
    printf("Lito 0 %i\n",l);
    lithosphere* l = platec_api_get_lithosphere(1);
    printf("Lito 1 %i\n",l);
    lithosphere* l = platec_api_get_lithosphere(2);
    printf("Lito 2 %i\n",l);    
    return 0;
}