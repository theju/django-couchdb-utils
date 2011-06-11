function(doc) { 
  emit([doc.server_url, doc.handle], doc);
}
