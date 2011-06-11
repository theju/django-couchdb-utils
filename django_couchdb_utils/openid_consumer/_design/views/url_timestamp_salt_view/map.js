function(doc) {
  emit([doc.server_url, doc.timestamp, doc.salt], doc);
}
