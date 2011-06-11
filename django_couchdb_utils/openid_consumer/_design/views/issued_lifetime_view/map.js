function(doc) {
  emit(doc.issued + doc.lifetime, doc);
}
