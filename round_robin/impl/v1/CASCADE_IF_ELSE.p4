#ifndef CASCADE_ELSE_DO
#define CASCADE_ELSE_DO
#endif

#define q 0
CASCADE_IF_DO {
    #define q 1
    CASCADE_IF_DO {
        #define q 2
        CASCADE_IF_DO {
            #define q 3
            CASCADE_IF_DO {
                #define q 4
                CASCADE_IF_DO {
                    #define q 5
                    CASCADE_IF_DO {
                        #define q 6
                        CASCADE_IF_DO {
                            #define q 7
                            CASCADE_IF_DO {
                                #define q
                                CASCADE_ELSE_DO
                            }
                        }
                    }
                }
            }
        }
    }
}
