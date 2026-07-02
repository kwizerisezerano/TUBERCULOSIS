content = open('app.py', 'r', encoding='utf-8').read()

me_route = """
@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user_me():
    identity = get_jwt_identity()
    if isinstance(identity, str) and identity.startswith('patient_'):
        patient_id = int(identity.split('_')[1])
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'msg': 'Not found'}), 404
        return jsonify({'patient': patient.to_dict()})
    else:
        user = User.query.get(int(identity))
        if not user:
            return jsonify({'msg': 'Not found'}), 404
        return jsonify({'user': user.to_dict()})

"""

marker = "@app.route('/api/auth/register'"
if "get_current_user_me" in content:
    print("Already inserted.")
else:
    content = content.replace(marker, me_route + marker, 1)
    open('app.py', 'w', encoding='utf-8').write(content)
    print("Done.")
