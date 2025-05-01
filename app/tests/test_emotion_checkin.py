
# Checks if the emotion-details page loads correctly when selected emotions are stored in the session
def test_emotion_selected(client, logged_in_user):
    with client.session_transaction() as sess:
        sess['selected_emotions'] = ['Relaxed::Calm']

    response = client.get('/emotion-details')
    assert b"Add more details to your emotion check-in" in response.data


# Checks if the user is redirected with a warning when no emotions are selected in the session.
def test_emotions_missing(client, logged_in_user):
    response = client.get('/emotion-details', follow_redirects=True)
    assert b"Please select emotions first." in response.data
    assert response.status_code == 200