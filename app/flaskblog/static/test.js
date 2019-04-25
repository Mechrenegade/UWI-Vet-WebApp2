window.onload = function(){
    console.log("Hello!!!!");
    let names = ['steffan', 'danny']
    let data = [{"id": 1, "descrip": "Pickup and hold dogs and cats for examination.", "rot_name": "Anatomic Path"}, {"id": 2, "descrip": "Routine Physical Examinations.", "rot_name": "Anatomic Path"}, {"id": 3, "descrip": "Apply a muzzle to a dog or cat.", "rot_name": "Anatomic Path"}, {"id": 4, "descrip": "Understand the use of different physical exams.", "rot_name": "Anatomic Path"}, {"id": 5, "descrip": "Auscultate and percuss the thorax.", "rot_name": "Anatomic Path"}, {"id": 6, "descrip": "Detect an apex beat and abnormal heart sounds.", "rot_name": "Anatomic Path"}, {"id": 7, "descrip": "Determine the age by examination of teeth", "rot_name": "Anatomic Path"}]
    $('#btn_click').on('click', (ev) => {
        console.log("I am clicked")
        const id = document.getElementById('student_search').value
        get_student(id)
        // for(let i=0; i<names.length; i++){
        //     let name = $('<h2>')
        //     name.append(names[i]);
        //     $('#root').append(name)
        // }
        create_table(data)
    })

    let get_data = () =>{
        $.ajax({
            "headers": {
                "accept": "application/json",
            },
            url: 'http://localhost:5000/rotations',
            method: 'GET', 
            success:(resp) => {
                create_table(JSON.parse(resp))
            }
        })
    }
    // get_data()


    // get_student();
    let create_table = (data) => {
        console.log(data)
        let table = $('<table>');
        let tr = $('<tr>').append('<th>id</th>').append('<th>descrip</th>').append('<th>rot_name</th>')
        table.append(tr)

        for(let i = 0; i<data.length; i++){
            const obj = data[i];
            let tr = $('<tr>').append(`<td>${obj['id']}</td><td>${obj['descrip']}</td><td>${obj['rot_name']}</td>`);
            table.append(tr)
        }
        $('#root').append(table)
    }
}

function get_student(){
    var id = $("#studentid").val()
    console.log(id);
    $.ajax({
        "headers": {
            "accept": "application/json",
        },
        url: '/student/'+id,
        method: 'GET', 
        success:(resp) => {
            
            // let text = $('<p>',{class:'test'}).append(resp)
            // $('#root').append(text)
            console.log(resp);
            $("#Name").html(resp.name)
            $("#ID").html(resp.id)
            $("#Date_enrolled").html(resp.date_enrolled)
            $("#Email").html(resp.email)
        }
    })
    $.ajax({
        "headers": {
            "accept": "application/json",
        },
        url: '/comp_rec/'+id,
        method: 'GET', 
        success:(resp) => {
            var output = " "
            for(var i =0; i<resp["data"].length; i++){
                output+="<tr>";
                output+="<td>"+resp["data"][i].student_id+"</td>"
                output+="<td>"+resp["data"][i].clinician_id+"</td>"
                output+="<td>"+resp["data"][i].comp_id+"</td>"
                //output+="<td>"+resp["data"][i].id+"</td>"
                if (resp["data"][i].mark==1){
                    output+="<td><input type='checkbox' name=''checked></td>";
                }
                else{
                    output+="<td><input type='checkbox' name='' id='chkbx'"+i+"'"+"></td>";
                }
                
                // output+="<td>"+resp["data"][i].mark+"</td>"
                
                output+="<td><button onclick='update("+resp["data"][i].id+","+i+")'>Update</button></td>"
                output+="</tr>"
            }
            $("#data").append(output)
            // let text = $('<p>',{class:'test'}).append(resp)
            // $('#root').append(text)
            console.log(resp);
        }
    })


}

function update(comp_id, chkbx_num){
    var x=$("#chkbx-"+chkbx_num).val();
    $.ajax({
        "headers": {
            "accept": "application/json",
        },
        url: '/update_rec/'+comp_id+'/'+x,
        method: 'GET', 
        success:(resp) => {
            console.log(x); 
            console.log(resp);
        }
    })
}