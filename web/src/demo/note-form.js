import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { Alert, Button } from 'reactstrap';

import styles from './index.scss';


export  default function NoteForm({
    onSubmit, errorMessage, noteId, title, body,
    onTitleChange, onBodyChange, loading, error}) {

    return <form onSubmit={onSubmit}>

        {loading && <div>Loading...</div>}

        {/* Error returned in the GraphQL response */}
        {errorMessage && <Alert color="danger">{errorMessage}</Alert>}

        {/* Error raised by client, eg. connection error... */}
        {error && <Alert color="danger">{error.message}</Alert>}

        <div>
            <input type="text" value={title} onChange={onTitleChange}
                   className={styles.inputField} />
        </div>
        <div>
            <textarea value={body} onChange={onBodyChange}
                      className={styles.textareaField}/>
        </div>
        <div>
            <Button type="submit" color="primary">
                {noteId ? 'Update note' : 'Create note'}
            </Button>{' '}
            {noteId && <Button tag={Link} to={`/note/${noteId}`} color="link">
                Cancel
            </Button>}
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
