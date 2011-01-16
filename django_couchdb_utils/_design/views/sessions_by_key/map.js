function(doc)
{
    if (doc.doc_type == 'Session')
    {
        emit(doc.key, null);
    }
}
