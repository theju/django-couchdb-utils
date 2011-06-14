function(doc) {
    if (doc.doc_type == 'Nonce') {
	emit([doc.server_url, doc.timestamp, doc.salt], doc);
    }
}
