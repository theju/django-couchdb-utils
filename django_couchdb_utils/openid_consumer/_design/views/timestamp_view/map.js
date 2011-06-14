function(doc) {
    if (doc.doc_type == 'Nonce') {
	emit(doc.timestamp, doc);
    }
}
