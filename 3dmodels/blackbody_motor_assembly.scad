





module mirrorplate(){
  difference(){
    union(){
      rotate([0,-45,0])
      difference(){
      translate([0,0,-5])
      cube([110,90,4], center=true);
      translate([-25,-20,-5]) cylinder(d=30, h=10, center=true);
      translate([25,-20,-5]) cylinder(d=30, h=10, center=true);
      translate([-25,20,-5]) cylinder(d=30, h=10, center=true);
      translate([25,20,-5]) cylinder(d=30, h=10, center=true);

      translate([52,30,-5]) cylinder(d=3, h=10, center=true);
      translate([52,-30,-5]) cylinder(d=3, h=10, center=true);

      translate([-52,30,-5]) cylinder(d=3, h=10, center=true);
      translate([-52,-30,-5]) cylinder(d=3, h=10, center=true);

      translate([40,42,-5]) cylinder(d=3, h=10, center=true);
      translate([40,-42,-5]) cylinder(d=3, h=10, center=true);

      translate([-40,42,-5]) cylinder(d=3, h=10, center=true);
      translate([-40,-42,-5]) cylinder(d=3, h=10, center=true);
      translate([55,45,0]) rotate([0,180,90]) corner(10,50);
      translate([55,-45,0]) rotate([0,180,0]) corner(10,50);
      translate([-55,45,0]) rotate([0,180,180]) corner(10,50);
      translate([-55,-45,0]) rotate([0,180,-90]) corner(10,50);
      }
      translate([49,0,-10]) cube([8,3,15], center=true);
      difference(){
        translate([0,0,0])
        rotate([0,90,0])
        cylinder(d=20, h=58);
        translate([0,0,-10])
        mirror();
        translate([0,0,-5])
        mirror();
        translate([0,0,0])
        mirror();
        translate([52,0,6])
        cylinder(d=3, h=10, center=true, $fn=6);
        translate([52,-6,0])
        rotate([90,0,0])
        cylinder(d=3, h=50, center=true, $fn=6);

      };
    };
    translate([20,0,0])
    rotate([0,90,0])
    cylinder(d=5.2, h=100, center=true, $fn=50);
  };
};

module corner(r, h) {
    translate([r / 2, r / 2, 0])
        difference() {
            cube([r + 0.01, r + 0.01, h], center = true);
            translate([r/2, r/2, 0])
                cylinder(r = r, h = h + 1, center = true);
        }
};


module motor(l=42,d=34,screwpar=30, screwd=3,axisd=5, axisl=20){
  translate([60,0,0]) rotate([90,0,-90])
  difference(){
    union(){
      translate([0,0,d/2+axisl/2]) cylinder(d=axisd, h=axisl, center=true, $fn=20);
      cube([l,l,d], center=true);
      }
      translate([screwpar/2,screwpar/2,0]) cylinder(d=screwd,h=l+2,center=true);
      translate([-screwpar/2,screwpar/2,0]) cylinder(d=screwd,h=l+2,center=true);
      translate([-screwpar/2,-screwpar/2,0]) cylinder(d=screwd,h=l+2,center=true);
      translate([screwpar/2,-screwpar/2,0]) cylinder(d=screwd,h=l+2,center=true);
    }
}

module mirror(){
  translate([-9,0,0])
  rotate([0,-45,0])
  cube([100,80,5], center=true);
};

module motorbase(){
  //translate([50,0,-60])
  //cube([150,100,5], center=true);
difference(){
    translate([50,0,-60])
    rotate([90,0,0])
    linear_extrude(height =60 , center = true, convexity = 10, twist = 0)
    polygon(points = [ [-20, 0], [20,0], [5,30], [-5,30]]);
     translate([35,-15,-41]) cube([20,20,30], center=true);
     translate([35,15,-41]) cube([20,20,30], center=true);
     translate([65,-15,-41]) cube([20,20,30], center=true);
     translate([65,15,-41]) cube([20,20,30], center=true);
     translate([61,15,-58]) cylinder(d=5, h=10, center=true);
     translate([61,-15,-58]) cylinder(d=5, h=10, center=true);
     translate([39,15,-58]) cylinder(d=5, h=10, center=true);
     translate([39,-15,-58]) cylinder(d=5, h=10, center=true);
    }
};

module motormount(){
  screwpar=30;
  screwd=5;
  union(){
  difference(){
    translate([50,0,-15])
    cube([10,60,85], center=true);

    rotate([0,90,0]) translate([screwpar/2,screwpar/2,50]) cylinder(d=screwd,h=20,center=true);
    rotate([0,90,0]) translate([-screwpar/2,screwpar/2,50]) cylinder(d=screwd,h=20,center=true);
    rotate([0,90,0]) translate([-screwpar/2,-screwpar/2,50]) cylinder(d=screwd,h=20,center=true);
    rotate([0,90,0]) translate([screwpar/2,-screwpar/2,50]) cylinder(d=screwd,h=20,center=true);
    rotate([0,90,0]) translate([0,0,50]) cylinder(d=30,h=20,center=true);
    translate([75,0,0]) rotate([90,0,-90]) cube([50,50,50], center=true);
  };
translate([0,0,-10]) motorbase();
};
};

module mirrorstrips() {
rotate([0,-45,0]) translate([-10,0,20])
difference(){
    translate([46,-36,-5]) rotate([0,0,45]) cube([25,10,2], center=true);
    translate([52,-30,-5]) cylinder(d=3, h=10, center=true, $fn=20);
    translate([40,-42,-5]) cylinder(d=3, h=10, center=true, $fn=20);
}
};

//#motor();
//#mirror();

mirrorstrips();

//rotate([$t*360,0,0]) 
translate([-10,0,0]) mirrorplate();
//	projection(cut=false) rotate([90,90,0]) 
motormount();

translate([80,0,-35])
#cube([10,60,70], center=true);