function(doc) { 
    if (doc.doc_type == 'Association') {
	emit([doc.server_url, doc.handle], doc);
    }
}
