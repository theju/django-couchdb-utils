function(doc) {
    if (doc.doc_type == 'UserOpenidAssociation') {
      emit(doc.openid, doc);
    }
}
