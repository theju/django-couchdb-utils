function (doc)
{
    if (doc.doc_type == 'User')
    {
        emit(doc.username, null);
    }
}
