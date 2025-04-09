import json

def txt_to_json(txt_filename, json_filename):
    """
    read a text file containing student info and convert it to a JSON file
    """
    students = []
    counter = 0  # Use for auto ID generation

    with open(txt_filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            counter += 1

            parts = line.split(' ', 1)
          
            if len(parts) == 1:
                name = parts[0]
                # Implement auto ID generation
                auto_id = f"{counter:08d}"
                student_info = {
                    "name": name,
                    "id": auto_id,
                    "timesCalled": 0,
                    "participation": 0.5,
                }
            elif len(parts) == 2:
                name, student_id = parts[0], parts[1]
                student_info = {
                    "name": name,
                    "id": student_id,
                    "timesCalled": 0,
                    "participation": 0.5,
                }
            else:
                print('Failed to parse info:', line)
                continue

            students.append(student_info)
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(students, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    txt_to_json("students_info.txt", "students_data.json")
    print("转换完成，已生成 students.json 文件。")
