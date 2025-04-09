from flask import Flask, jsonify, render_template, request
import subprocess
import json
import random

app = Flask(__name__)

def calculate_weights(students):
    """
    Use this function to calculate the weights for each student based on their timesCalled and participation.
    The weights are calculated as follows:
        - If the student has been called more times than the average, their weight is inversely proportional to their call ratio;
        - If the student has been called fewer times than the average, their weight is 1;
        - The final weight is then adjusted by multiplying with 1/(1+participation*10).
    """
    n = len(students)
    total_times_called = sum(student['timesCalled'] for student in students)
    
    if total_times_called == 0:
        base_weights = [1] * n
    else:
        avg_ratio = 1 / n
        base_weights = []
        for student in students:
            ratio = student['timesCalled'] / total_times_called
            if ratio > avg_ratio:
                weight = avg_ratio / ratio
            else:
                weight = 1
            base_weights.append(weight)
    
    final_weights = []
    for i, student in enumerate(students):
        participation = student.get("participation", 0)
        factor = 1 / (1 + participation)
        final_weights.append(base_weights[i] * factor)
    
    return final_weights

@app.route('/')
def index():
    return render_template('students.html')

@app.route('/import_students_info', methods=['POST'])
def import_students_info():
    try:
        subprocess.run(['python', 'import_students_info.py'], check=True)
        return jsonify({"message": "数据导入成功！"})
    except subprocess.CalledProcessError as e:
        return jsonify({"message": f"导入失败，错误信息：{e}"}), 500

@app.route('/pick', methods=['GET'])
def pick():
    """
    Pick a student randomly based on their weights.
    The weights are calculated based on the number of times called and their participation.
    """
    try:
        with open("students_data.json", "r", encoding="utf-8") as f:
            students = json.load(f)
        
        if not students:
            return jsonify({"message": "学生数据为空"}), 500
        
        weights = calculate_weights(students)
        selected = random.choices(students, weights=weights, k=1)[0]
        selected['timesCalled'] += 1

        with open("students_data.json", "w", encoding="utf-8") as f:
            json.dump(students, f, ensure_ascii=False, indent=4)
        
        return jsonify({
            "name": selected["name"],
            "id": selected["id"],
            "timesCalled": selected["timesCalled"],
            "participation": selected.get("participation", 0)
        })
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return jsonify({"message": f"学生数据未找到或文件格式错误: {e}"}), 500
    except Exception as e:
        return jsonify({"message": f"出现错误: {e}"}), 500

@app.route('/update_participation', methods=['POST'])
def update_participation():
    """
    Update the participation of a student based on their attendance status.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "缺少请求数据"}), 400
        
        student_id = data.get("id")
        absent = data.get("absent")
        if student_id is None or absent is None:
            return jsonify({"message": "缺少学生 id 或 attendance 数据"}), 400
        
        with open("students_data.json", "r", encoding="utf-8") as f:
            students = json.load(f)
        
        student_found = False
        step = 0.1
        for student in students:
            if student["id"] == student_id:
                current_participation = student.get("participation", 0)
                if absent:
                    new_participation = max(0, current_participation - step)
                else:
                    new_participation = min(1, current_participation + step)
                student["participation"] = new_participation
                student_found = True
                break
        
        if not student_found:
            return jsonify({"message": "未找到对应的学生数据"}), 404
        
        with open("students_data.json", "w", encoding="utf-8") as f:
            json.dump(students, f, ensure_ascii=False, indent=4)
        
        status = "缺勤" if absent else "到场"
        return jsonify({"message": f"根据 {status} 状态更新参与度成功！", "new_participation": student.get("participation")})
    except Exception as e:
        return jsonify({"message": f"更新失败: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
