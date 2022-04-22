#ifndef CASCADE_ELSE_DO
#define CASCADE_ELSE_DO
#endif

#ifndef q
#else
#undef q
#endif

#define q 7
CASCADE_IF_DO {
    #undef q
    #define q 6
    CASCADE_IF_DO {
        #undef q
        #define q 5
        CASCADE_IF_DO {
            #undef q
            #define q 4
            CASCADE_IF_DO {
                #undef q
                #define q 3
                CASCADE_IF_DO {
                    #undef q
                    #define q 2
                    CASCADE_IF_DO {
                        #undef q
                        #define q 1
                        CASCADE_IF_DO {
                            #undef q
                            #define q 0
                            CASCADE_IF_DO {
                                CASCADE_ELSE_DO
                            }
                        }
                    }
                }
            }
        }
    }
}
