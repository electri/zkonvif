/*
 * relizing circular queue
*/
#define MAXLEN = 1024

struct  List
{
	unsigned char buf[MAXLEN];
	int begin;
	int end;
};

void circque_init(struct List *plist);

int circque_get_len(struct List *plist);

void circque_push(struct List *plist, char ch);

int circque_pop(struct List *plist);

int circque_front(struct List *plist, unsigned char *lch);

int circque_back(struct List *plist, unsigned char *lch);
