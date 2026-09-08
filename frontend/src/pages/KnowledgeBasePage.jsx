import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

export default function KnowledgeBasePage() {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [queryText, setQueryText] = useState('');
  const [queryResults, setQueryResults] = useState(null);
  const [querying, setQuerying] = useState(false);

  const [textDoc, setTextDoc] = useState({
    title: '',
    content: '',
    document_type: 'guideline'
  });
  const [showAddForm, setShowAddForm] = useState(false);

  const loadDocs = async () => {
    try {
      setLoading(true);
      const data = await api.getKnowledgeDocs();
      setDocs(data);
    } catch (err) {
      console.error('Failed to load knowledge docs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', 'guideline');

    setUploading(true);
    try {
      await api.uploadKnowledge(formData);
      await loadDocs();
      alert(`Knowledge document '${file.name}' chunked and indexed successfully!`);
    } catch (err) {
      alert('Upload failed: ' + err.message);
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleCreateTextDoc = async (e) => {
    e.preventDefault();
    try {
      await api.uploadKnowledge({
        title: textDoc.title,
        content: textDoc.content,
        document_type: textDoc.document_type
      });
      setTextDoc({ title: '', content: '', document_type: 'guideline' });
      setShowAddForm(false);
      await loadDocs();
    } catch (err) {
      alert('Failed to save document: ' + err.message);
    }
  };

  const handleDelete = async (docId) => {
    if (!window.confirm('Delete this knowledge document and its chunks?')) return;
    try {
      await api.deleteKnowledgeDoc(docId);
      await loadDocs();
    } catch (err) {
      alert('Delete failed: ' + err.message);
    }
  };

  const handleQuery = async (e) => {
    e.preventDefault();
    if (!queryText.trim()) return;
    try {
      setQuerying(true);
      const results = await api.queryKnowledge(queryText);
      setQueryResults(results);
    } catch (err) {
      alert('Query failed: ' + err.message);
    } finally {
      setQuerying(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem' }}>Hiring Knowledge Base (Lightweight RAG)</h2>
          <p style={{ color: '#9ca3af', fontSize: '0.88rem' }}>
            Store internal competency frameworks, interview guidelines, and recruitment policies
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <input
            type="file"
            id="knowledgeDocUpload"
            style={{ display: 'none' }}
            accept=".pdf,.docx,.txt"
            onChange={handleFileUpload}
            disabled={uploading}
          />
          <button
            className="btn btn-primary"
            onClick={() => document.getElementById('knowledgeDocUpload').click()}
            disabled={uploading}
          >
            {uploading ? 'Chunking & Indexing...' : '+ Upload Document (PDF/DOCX/TXT)'}
          </button>
        </div>
      </div>

      {/* RAG Query Tester Card */}
      <div className="card" style={{ marginBottom: '32px', borderColor: 'rgba(99, 102, 241, 0.3)' }}>
        <div className="card-header">
          <h3 className="card-title">Test RAG Semantic Retrieval</h3>
          <span style={{ fontSize: '0.82rem', color: '#9ca3af' }}>TF-IDF & Cosine Similarity over Document Chunks</span>
        </div>

        <form onSubmit={handleQuery} style={{ display: 'flex', gap: '12px' }}>
          <input
            type="text"
            className="form-input"
            placeholder="e.g. What are the requirements for junior backend engineers regarding cloud experience?"
            value={queryText}
            onChange={(e) => setQueryText(e.target.value)}
            style={{ flex: 1 }}
          />
          <button type="submit" className="btn btn-primary" disabled={querying}>
            {querying ? 'Retrieving...' : '🔍 Query RAG'}
          </button>
        </form>

        {queryResults && (
          <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--border-color)' }}>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '12px', color: '#34d399' }}>
              Retrieved Context ({queryResults.length} Chunks Matched):
            </div>
            {queryResults.length === 0 ? (
              <div style={{ color: '#9ca3af', fontSize: '0.86rem' }}>No matching chunks exceeded relevance threshold.</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {queryResults.map((r, idx) => (
                  <div key={idx} style={{ background: 'rgba(0,0,0,0.25)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span style={{ fontWeight: 600, color: '#818cf8', fontSize: '0.85rem' }}>
                        Source: {r.document_title} ({r.document_type})
                      </span>
                      <span style={{ fontSize: '0.78rem', color: '#34d399' }}>
                        Similarity: {(r.similarity_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <p style={{ fontSize: '0.85rem', color: '#d1d5db' }}>{r.content}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Indexed Documents Table */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Indexed Knowledge Documents ({docs.length})</h3>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '30px 0', color: '#9ca3af' }}>Loading knowledge base...</div>
        ) : docs.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 0', color: '#9ca3af' }}>
            No knowledge documents indexed yet. Upload a company hiring guideline or competency framework to enable RAG.
          </div>
        ) : (
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Document Title</th>
                  <th>Category</th>
                  <th>Indexed Chunks</th>
                  <th>Filename</th>
                  <th>Created At</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {docs.map((doc) => (
                  <tr key={doc.id}>
                    <td>
                      <strong style={{ color: '#f3f4f6' }}>{doc.title}</strong>
                    </td>
                    <td>
                      <span className="badge badge-skill">{doc.document_type}</span>
                    </td>
                    <td>
                      <span style={{ fontWeight: 600, color: '#818cf8' }}>{doc.chunks_count} chunks</span>
                    </td>
                    <td style={{ color: '#9ca3af', fontSize: '0.82rem' }}>
                      {doc.filename || 'Direct Text Input'}
                    </td>
                    <td style={{ color: '#9ca3af', fontSize: '0.82rem' }}>
                      {new Date(doc.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(doc.id)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
