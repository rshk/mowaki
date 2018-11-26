import React from 'react';
import PropTypes from 'prop-types';
import {Redirect} from 'react-router-dom';
import gql from 'graphql-tag';
import {Mutation} from 'react-apollo';

import styles from './index.scss';


const MUTATION_DELETE_NOTE = gql`
    mutation deleteNote($id: Int!) {
        deleteNote(id: $id) {
            ok
        }
    }
`;


export default class DeleteNoteButton extends React.Component {
    static propTypes = {
        noteId: PropTypes.number.isRequired,
    };

    constructor(...args) {
        super(...args);
        this.state = {
            success: false,
        };
    }

    render() {
        return <Mutation mutation={MUTATION_DELETE_NOTE}>
            {this._renderButton.bind(this)}
        </Mutation>;
    }

    _renderButton(deleteNote) {
        if (this.state.success) {
            return <Redirect to="/" />;
        }
        return <button type="button"
                       className={`${styles.button} ${styles['button--danger']}`}
                       onClick={this._onClick.bind(this, deleteNote)}>
            Delete note
        </button>;
    }

    _onClick(deleteNote) {
        const {noteId} = this.props;
        deleteNote({variables: {id: noteId}})
            .then(({data: {deleteNote: {ok}}}) => {
                if (ok) {
                    this.setState({success: true});
                }
            });
    }

}
