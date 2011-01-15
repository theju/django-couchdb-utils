function(doc)
{
    if(doc.doc_type == 'CacheRow')
    {
        emit(doc.key, null);
    }
}
