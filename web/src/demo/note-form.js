import React from 'react';
import PropTypes from 'prop-types';
import {Link} from 'react-router-dom';

import styles from './index.scss';


export  default function NoteForm({
    onSubmit, errorMessage, noteId, title, body,
    onTitleChange, onBodyChange, loading, error}) {

    return <form onSubmit={onSubmit}>

        {loading && <div>Loading...</div>}

        {/* Error returned in the GraphQL response */}
        {errorMessage && <div><strong>Error:</strong> {errorMessage}</div>}

        {/* Error raised by client, eg. connection error... */}
        {error && <div><strong>Error:</strong> {error.message}</div>}

        <div>
            <input type="text" value={title} onChange={onTitleChange}
                   className={styles.inputField} />
        </div>
        <div>
            <textarea value={body} onChange={onBodyChange}
                      className={styles.textareaField}/>
        </div>
        <div>
            <button type="submit" className={styles.button}>
                {noteId ? 'Update note' : 'Create note'}
            </button>{' '}
            {noteId && <Link to={`/note/${noteId}`}>Cancel</Link>}
        </div>
    </form>;
}


NoteForm.propTypes = {
    onSubmit: PropTypes.func.isRequired,
    errorMessage: PropTypes.string,
    noteId: PropTypes.number,  // Update form only
    title: PropTypes.string.isRequired,
    body: PropTypes.string.isRequired,
    onTitleChange: PropTypes.func.isRequired,
    onBodyChange: PropTypes.func.isRequired,
};
