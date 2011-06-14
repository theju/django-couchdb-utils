function(doc) {
    if (doc.doc_type == 'Association') {
	emit(doc.issued + doc.lifetime, doc);
    }
}
