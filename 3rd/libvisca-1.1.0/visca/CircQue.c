#include  CircQue.h
void circque_init(struct LIst *plist)
{
	plist->begin = plist->end = -1;
}

int circque_get_len(struct List *plist)
{
	if (plist->begin = -1)
		return 0;
	else {
		if (p->end < p->begin) {
			int	end = p-> end + MAXLEN;
			return end - p->start + 1;
void circque_push(struct List *plist, char ch)
{
	if (plist->begin = -1) {
		plist->begin = plist->end = 0;
		*(plist + 0) = ch;
	}
	else {
		plist->end++;
		plist->end = plist->end % MAXLEN; 
		*(plist + plist->end) = ch;
		if (plist->begin == plist->end) {
			plist->begin++;
			plist->begin = plist->begin % MAXLEN; 
		}
}

int circque_pop(struct List *plist)
{
	if (plist->begin == -1)
		return -1;
	if (plist->begin == plist->end) {
		plist->begin == plist->end = -1;
		return 0;
	}
	plist->begin = plist->begin++ % MAXLEN;
	return 0;
}

int circque_front(struct List *plist, unsigned char *lch)
{
	if (plist->begin == -1)
		return 0;
	else {
		*lch = *(plist + plist->begin);
		return 0;
	}
}

int circque_back(struct List *plist, unsigned char *lch)
{
	if (plist->end == -1)
		return 0;
	else {
		*lch = *(plist + plist->end);
		return 1;
	}
}
